"""Repairs flow for System Log Monitor."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.repairs import RepairsFlow, RepairsFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.selector import SelectOptionDict, SelectSelector, SelectSelectorConfig

from .const import CONF_IGNORED_ISSUES, DOMAIN


class SystemLogRepairFlow(RepairsFlow):
    """Handler for system log issue fixing flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> RepairsFlowResult:
        """First page: Show details, log reference link, and 3 specific repair action choices."""
        issue_entry = ir.async_get(self.hass).issues.get((DOMAIN, self.issue_id))
        data = issue_entry.data if issue_entry and issue_entry.data else {}

        message = data.get("message", "No log details available.")
        domain = data.get("domain", "unknown")

        logs_url = "/config/logs"

        if user_input is not None:
            action = user_input.get("action_choice")

            if action == "github":
                return await self.async_step_github()

            if action == "fixed":
                ir.async_delete_issue(self.hass, DOMAIN, self.issue_id)
                return self.async_create_entry(title="", data={})

            if action == "ignore":
                fingerprint = data.get("fingerprint", "")
                entries = self.hass.config_entries.async_entries(DOMAIN)
                for entry in entries:
                    current_options = dict(entry.options)
                    if not current_options:
                        current_options = dict(entry.data)

                    ignored = list(current_options.get(CONF_IGNORED_ISSUES, []))
                    if fingerprint and fingerprint not in ignored:
                        ignored.append(fingerprint)
                        current_options[CONF_IGNORED_ISSUES] = ignored
                        self.hass.config_entries.async_update_entry(
                            entry, options=current_options
                        )

                ir.async_delete_issue(self.hass, DOMAIN, self.issue_id)
                return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("action_choice"): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(
                                value="github", label="Report as github issue"
                            ),
                            SelectOptionDict(
                                value="fixed",
                                label="I've fixed this, tell me if it happens again",
                            ),
                            SelectOptionDict(
                                value="ignore", label="Ignore this log message"
                            ),
                        ]
                    )
                )
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={
                "domain": domain,
                "message": message,
                "logs_url": logs_url,
            },
        )

    async def async_step_github(
        self, user_input: dict[str, Any] | None = None
    ) -> RepairsFlowResult:
        """Secondary step with GitHub issue link and log details."""
        if user_input is not None:
            ir.async_delete_issue(self.hass, DOMAIN, self.issue_id)
            return self.async_create_entry(title="", data={})

        issue_entry = ir.async_get(self.hass).issues.get((DOMAIN, self.issue_id))
        data = issue_entry.data if issue_entry and issue_entry.data else {}

        return self.async_show_form(
            step_id="github",
            data_schema=vol.Schema({}),
            description_placeholders={
                "message": data.get("message", "No log details available."),
                "github_url": "https://github.com/issues/new",
            },
        )


class SystemLogRedirectRepairFlow(RepairsFlow):
    """Fallback flow if required."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> RepairsFlowResult:
        return self.async_create_entry(title="", data={})


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, Any] | None,
) -> RepairsFlow:
    """Create flow for handling repairs."""
    return SystemLogRepairFlow()