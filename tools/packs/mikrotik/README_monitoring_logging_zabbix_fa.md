# MikroTik Monitoring, Logging and Zabbix — Chapter 22

## وضعیت
- Content package: authored; review required.
- Lab execution: designed, not executed.
- Fixture strings are synthetic and are **not** real RouterOS output.
- No claim is made that a Zabbix XML template has been imported or validated.
- Target versions must be recorded before deployment (RouterOS, Zabbix Server, Agent/Agent2, Linux/rsyslog).

## مسیر پیشنهادی Syslog
RouterOS (UDP/514, restricted source) → Linux collector/rsyslog → per-device log file → Zabbix Agent log monitoring → item/trigger/action.

### نکات مهم
1. Restrict UDP/514 at the network firewall to known router addresses; never expose it publicly.
2. Configure a remote logging action and specific topics from RouterOS WebFig/WinBox, then generate one low-risk test event.
3. On the collector: `sudo tcpdump -ni any udp port 514`; `sudo systemctl status rsyslog --no-pager`; `sudo journalctl -u rsyslog --since '10 minutes ago'`.
4. Verify file writes and permissions independently: `stat /var/log/mikrotik/DEVICE.log`; `tail -n 50 /var/log/mikrotik/DEVICE.log`.
5. Only then verify Zabbix latest data, item key, agent read permissions and rotation behavior.
6. Add meaningful triggers only; define heartbeat/expected log rate before alerting on silence.
7. Test positive and negative fixtures on a non-production Zabbix instance of the exact target version before deployment.

## Safety and release
- Keep credentials, tokens and unredacted exports out of Git.
- Back up config and establish alternate management access before changing a remote router.
- Run a pilot on one non-critical router and document rollback.
- Mark tests `passed` only with timestamped evidence, exact versions and expected-vs-actual results.

## Content
The compatible learning pack is `routeros_monitoring_logging_zabbix_ch22_pack.json`, with five L0–L4 lessons and answer keys inside each lesson's `meta_json`.
