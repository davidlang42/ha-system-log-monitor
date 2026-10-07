"""Config flow for System Log Monitor."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_IGNORED_ISSUES,
    CONF_LOG_ERRORS,
    CONF_LOG_WARNINGS,
    DEFAULT_IGNORED_ISSUES,
    DEFAULT_LOG_ERRORS,
    DEFAULT_LOG_WARNINGS,
    DOMAIN,
)


class SystemLogMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for System Log Monitor."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title="System Log Monitor",
                data={
                    CONF_LOG_ERRORS: user_input.get(CONF_LOG_ERRORS, DEFAULT_LOG_ERRORS),
                    CONF_LOG_WARNINGS: user_input.get(CONF_LOG_WARNINGS, DEFAULT_LOG_WARNINGS),
                    CONF_IGNORED_ISSUES: DEFAULT_IGNORED_ISSUES,
                },
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_LOG_ERRORS, default=DEFAULT_LOG_ERRORS): bool,
                vol.Required(CONF_LOG_WARNINGS, default=DEFAULT_LOG_WARNINGS): bool,
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow handler."""
        return SystemLogMonitorOptionsFlow(config_entry)


class SystemLogMonitorOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for System Log Monitor."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage options and configuration modifications including ignore list management."""
        current_options = {**self.config_entry.data, **self.config_entry.options}
        ignored_issues = current_options.get(CONF_IGNORED_ISSUES, [])

        if user_input is not None:
            selected_ignored = user_input.get(CONF_IGNORED_ISSUES, [])
            updated_ignored = [item for item in ignored_issues if item in selected_ignored]

            new_options = {
                CONF_LOG_ERRORS: user_input.get(CONF_LOG_ERRORS, DEFAULT_LOG_ERRORS),
                CONF_LOG_WARNINGS: user_input.get(CONF_LOG_WARNINGS, DEFAULT_LOG_WARNINGS),
                CONF_IGNORED_ISSUES: updated_ignored,
            }

            # Return options properly instead of mutating entry data manually
            return self.async_create_entry(title="", data=new_options)

        ignore_schema = {}
        if ignored_issues:
            ignore_schema[
                vol.Optional(
                    CONF_IGNORED_ISSUES,
                    default=ignored_issues,
                )
            ] = cv.multi_select({item: item for item in ignored_issues})

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_LOG_ERRORS,
                    default=current_options.get(CONF_LOG_ERRORS, DEFAULT_LOG_ERRORS),
                ): bool,
                vol.Required(
                    CONF_LOG_WARNINGS,
                    default=current_options.get(CONF_LOG_WARNINGS, DEFAULT_LOG_WARNINGS),
                ): bool,
                **ignore_schema,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            description_placeholders={"count": str(len(ignored_issues))},
        )