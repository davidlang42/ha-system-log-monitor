"""The System Log Monitor integration."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir

from .const import (
    CONF_IGNORED_ISSUES,
    CONF_LOG_ERRORS,
    CONF_LOG_WARNINGS,
    DEFAULT_IGNORED_ISSUES,
    DEFAULT_LOG_ERRORS,
    DEFAULT_LOG_WARNINGS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up System Log Monitor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = {**entry.data, **entry.options}
    hass.data[DOMAIN][entry.entry_id] = config

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Intercept system_log records via event bus listener
    @callback
    def async_handle_system_log(event):
        """Handle incoming system log events."""
        conf = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
        log_errors = conf.get(CONF_LOG_ERRORS, DEFAULT_LOG_ERRORS)
        log_warnings = conf.get(CONF_LOG_WARNINGS, DEFAULT_LOG_WARNINGS)
        ignored_list = conf.get(CONF_IGNORED_ISSUES, DEFAULT_IGNORED_ISSUES)

        level = event.data.get("level")
        if level == "ERROR" and not log_errors:
            return
        if level == "WARNING" and not log_warnings:
            return
        if level not in ("ERROR", "WARNING"):
            return

        message = event.data.get("message", "")
        if isinstance(message, tuple | list):
            message = " ".join(str(m) for m in message)
        else:
            message = str(message)

        source = event.data.get("source", ["unknown"])
        domain = source[0] if isinstance(source, list) and source else "unknown"

        # Unique fingerprint representation for de-duplication
        fingerprint = f"{domain}:{message[:100]}"

        if fingerprint in ignored_list:
            return

        # Build helpful title
        first_line = message.splitlines()[0] if message else "Empty message"
        title_prefix = f"[{domain.upper()}]" if domain and domain != "unknown" else "[System]"
        title = f"{title_prefix} {first_line}"
        if len(title) > 90:
            title = title[:87] + "..."

        issue_id = f"log_{abs(hash(fingerprint))}"

        # Register repair issue
        ir.async_create_issue(
            hass,
            domain=DOMAIN,
            issue_id=issue_id,
            is_fixable=True,
            is_persistent=False,
            severity=ir.IssueSeverity.ERROR if level == "ERROR" else ir.IssueSeverity.WARNING,
            translation_key="log_issue",
            translation_placeholders={
                "title": title,
                "domain": domain,
                "message": message,
                "fingerprint": fingerprint,
            },
        )

    # Listen to system_log events emitted natively by Home Assistant core
    entry.async_on_unload(
        hass.bus.async_listen("system_log_event", async_handle_system_log)
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)