from contextvars import ContextVar

saya_instance = ContextVar("saya_instance")
channel_instance = ContextVar("channel")

environment_metadata = ContextVar("environment_metadata")
