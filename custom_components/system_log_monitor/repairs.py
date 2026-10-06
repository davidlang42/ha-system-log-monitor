"""Repairs flow for System Log Monitor."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.repairs import RepairsFlow, RepairsFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from .const import CONF_IGNORED_ISSUES, DOMAIN


async class SystemLogRepairFlow(RepairsFlow):
    """Handler for system log issue fixing flow."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> RepairsFlowResult:
        """First page: Show details, log reference link, and 3 specific repair action choices."""
        issue_entry = ir.async_get(self.hass).issues.get((DOMAIN, self.issue_id))
        data = issue_entry.data if issue_entry and issue_entry.data else {}
        
        message = data.get("message", "No log details available.")
        domain = data.get("domain", "unknown")
        fingerprint = data.get("fingerprint", "")

        # External URL formatting links
        logs_url = "/config/logs"
        github_issues_url = "https://github.com/issues/new"

        if user_input is not None:
            action = user_input.get("action_choice")

            if action == "github":
                return self.async_abort(
                    reason="redirect_github",
                    next_flow=None,
                )
            
            if action == "fixed":
                # Dismiss repair issue permanently until it reappears
                ir.async_delete_issue(self.hass, DOMAIN, self.issue_id)
                return self.async_create_entry(title="", data={})

            if action == "ignore":
                # Add fingerprint to ignore list across config entries
                for entry_id, conf in self.hass.data.get(DOMAIN, {}).items():
                    ignored = list(conf.get(CONF_IGNORED_ISSUES, []))
                    if fingerprint and fingerprint not in ignored:
                        ignored.append(fingerprint)
                        conf[CONF_IGNORED_ISSUES] = ignored
                        
                        # Save entry update persistently
                        entry = self.hass.config_entries.async_get_entry(entry_id)
                        if entry:
                            new_data = {**entry.data, CONF_IGNORED_ISSUES: ignored}
                            self.hass.config_entries.async_update_entry(entry, data=new_data)

                # Delete current issue instance
                ir.async_delete_issue(self.hass, DOMAIN, self.issue_id)
                return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("action_choice"): vol.In(
                    {
                        "github": "Report as github issue",
                        "fixed": "I've fixed this, tell me if it happens again",
                        "ignore": "Ignore this log message",
                    }
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
                "github_url": github_issues_url,
            },
        )


async class SystemLogRedirectRepairFlow(RepairsFlow):
    """Fallback flow if required."""
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> RepairsFlowResult:
        return self.async_create_entry(title="", data={})


async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, Any] | None,
) -> RepairsFlow:
    """Create flow for handling repairs."""
    return SystemLogRepairFlow()