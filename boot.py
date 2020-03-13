try:
    import uasyncio
except Exception:
    import upip
    import wifi_connect
    from machine import reset
    wifi_connect.connect()
    upip.install('micropython-uasyncio')
    reset()
