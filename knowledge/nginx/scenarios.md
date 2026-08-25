# Nginx 场景卡

## SC-NGX-001：API 网关前的限流改造

**输入。** `/login` 和 `/search` 的突发流量导致上游不稳定；用户分布在共享 NAT 与企业代理之后。

**责任路由。** `platform-sre-engineer` 负责流量、上游饱和和发布；`backend-runtime-engineer` 负责重试/幂等和身份头契约；`product-discovery-manager` 确认用户影响与例外需求；`quality-engineer` 负责压测和错误恢复验证。

**通过条件。** 先以 dry-run 量化键分布和误伤；按端点定义限流行为和状态码；验证共享 NAT、客户端重试、恶意流量、上游不可用与回滚。禁止仅按 `$remote_addr` 直接全局上线。

## SC-NGX-002：上游发布造成 P99 上升

**输入。** 新应用版本发布后，部分 upstream 响应慢，Nginx 连接和临时文件磁盘使用升高。

**通过条件。** 区分上游慢、缓冲策略、慢客户端、重试放大和资源饱和；验证 `proxy_*_timeout`、缓冲、上游策略与幂等；恢复策略不能产生重复写入。参见 KC-NGX-001 与 KC-NGX-002。
