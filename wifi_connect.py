def connect():
    import network
    from config import config
    
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(config['ssid'], config['wifi_pw'])
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())