inspired by https://github.com/kverpoorten/TelegramChannelAggregator/tree/main

## run as service

Place TelegramForwarder.service in `/etc/systemd/system/` and 

```shell
systemctl daemon-reload
systemctl enable TelegramForwarder.service
systemctl start TelegramForwarder.service
systemctl status TelegramForwarder.service
```
