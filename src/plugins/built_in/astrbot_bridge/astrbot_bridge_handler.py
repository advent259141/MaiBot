"""AstrBot Bridge ON_START EventHandler

在MaiBot启动时注册WS自定义消息处理器，接收来自AstrBot的tool_sync和tool_result消息。
"""

from typing import Tuple, Optional

from src.common.logger import get_logger
from src.plugin_system.base.base_events_handler import BaseEventHandler
from src.plugin_system.base.component_types import EventType, MaiMessages, CustomEventHandlerResult

logger = get_logger("astrbot_bridge_handler")


class AstrBotBridgeInitHandler(BaseEventHandler):
    """ON_START事件处理器 — 注册tool_sync和tool_result自定义消息处理器"""

    event_type = EventType.ON_START
    handler_name = "astrbot_bridge_init"
    handler_description = "在启动时注册AstrBot工具桥接的WS消息处理器"
    weight = 0

    async def execute(
        self, message: MaiMessages | None
    ) -> Tuple[bool, bool, Optional[str], Optional[CustomEventHandlerResult], Optional[MaiMessages]]:
        """在ON_START时初始化工具桥接"""
        try:
            from src.common.message import get_global_api
            from src.plugins.built_in.astrbot_bridge.tool_bridge import (
                _handle_tool_sync_ws, _handle_tool_result_ws,
            )

            api = get_global_api()

            # Register on the API Server layer (server_ws_api.py custom_handlers)
            # Messages with type="custom_tool_sync" / "custom_tool_result" are
            # dispatched by server_ws_api.py to config.custom_handlers[type]
            extra_server = getattr(api, "extra_server", None)
            if extra_server and hasattr(extra_server, "config"):
                extra_server.config.custom_handlers["custom_tool_sync"] = _handle_tool_sync_ws
                extra_server.config.custom_handlers["custom_tool_result"] = _handle_tool_result_ws
                logger.info("[AstrBot Bridge] 工具桥接初始化成功 (API Server custom_handlers)")
            else:
                # Fallback: register on MessageServer layer (legacy mode)
                from src.plugins.built_in.astrbot_bridge.tool_bridge import init_astrbot_tool_bridge
                init_astrbot_tool_bridge(api)
                logger.info("[AstrBot Bridge] 工具桥接初始化成功 (MessageServer fallback)")

            return True, True, None, None, None
        except Exception as e:
            logger.error(f"[AstrBot Bridge] 工具桥接初始化失败: {e}", exc_info=True)
            return False, True, None, None, None
