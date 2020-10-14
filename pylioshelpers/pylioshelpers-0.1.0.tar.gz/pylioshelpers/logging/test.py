from logging import log

log("test - no level")

log("test ok", "ok")
log("test success", "success")
log("test info", "info")
log("test warn", "warn")
log("test error", "error")
log("test message", "message")

log(
    {
        "test": "message",
        "a": "b",
        "c": "d",
        "test_array": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k"],
    },
    "warn",
)
log([1, 2, 3, 4, 5], "info")
