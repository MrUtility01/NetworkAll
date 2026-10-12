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


## Chapter 23 — Operational Zabbix scenarios

The companion learning pack is `routeros_zabbix_operations_ch23_pack.json`. It contains five staged lessons (L0–L4) covering the telemetry model, interface counter math, robust Trigger/Recovery logic, Syslog correlation/RCA, and capacity/SLO/safe rollout. The answer keys are separate from question prompts inside each lesson's `meta_json`.

### Acceptance matrix (lab pending)

| Case | Controlled input | Expected classification | Evidence to retain |
|---|---|---|---|
| Healthy traffic | 500,000-octet delta over 10 seconds | 400,000 bit/s; no capacity alarm by itself | Raw counter values, sample timestamps, calculation |
| Counter discontinuity | Counter drops from 9,000,000 to 1,000 | Invalid delta until reset/rollover is handled | Device uptime, counter values, interface identity |
| Stale telemetry | Last data age exceeds multiple polling intervals | Telemetry/collection problem, not proof that device is healthy | Latest data time, item status, agent/server logs |
| Link flap | Synthetic down/up events eight seconds apart | Correlation required; root cause unconfirmed | Timestamped event sequence and independent peer evidence |
| Log pipeline break | File receives messages but Zabbix item is stale | Inspect ACL, rotation, agent permissions, item and preprocessing | File stat/tail, service logs, item status |

These are synthetic test fixtures, not real router captures. Record exact RouterOS, Zabbix Server/Proxy/Agent and collector versions before executing. A test is passed only with timestamped evidence and expected-versus-actual results.

### Operational constraints

- This pack is a curriculum package, not an importable Zabbix XML/YAML template. Do not import it as a template.
- Trigger expressions, preprocessing and item keys must be validated against the exact Zabbix release.
- Restrict UDP/514 to known source addresses and the management network; do not expose it to the public Internet.
- Never commit SNMP communities, API tokens, credentials, unredacted router exports or private logs.
- Lab status remains `designed_not_executed`; content status remains `review_required` until a real lab run is evidenced.
