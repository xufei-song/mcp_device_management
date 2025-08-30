"""
内存事件存储，用于演示断点续传功能
参考官方SDK示例实现
"""

import logging
from collections import deque
from dataclasses import dataclass
from uuid import uuid4

from mcp.server.streamable_http import EventCallback, EventId, EventMessage, EventStore, StreamId
from mcp.types import JSONRPCMessage

logger = logging.getLogger(__name__)


@dataclass
class EventEntry:
    """事件条目"""
    event_id: EventId
    stream_id: StreamId
    message: JSONRPCMessage


class InMemoryEventStore(EventStore):
    """
    内存事件存储，用于支持断点续传功能
    生产环境建议使用持久化存储
    """

    def __init__(self, max_events_per_stream: int = 100):
        """初始化事件存储
        
        Args:
            max_events_per_stream: 每个流保存的最大事件数
        """
        self.max_events_per_stream = max_events_per_stream
        # 每个流维护最后N个事件
        self.streams: dict[StreamId, deque[EventEntry]] = {}
        # event_id -> EventEntry 快速查找
        self.event_index: dict[EventId, EventEntry] = {}

    async def store_event(self, stream_id: StreamId, message: JSONRPCMessage) -> EventId:
        """存储事件并生成事件ID"""
        event_id = str(uuid4())
        event_entry = EventEntry(event_id=event_id, stream_id=stream_id, message=message)

        # 获取或创建流的事件队列
        if stream_id not in self.streams:
            self.streams[stream_id] = deque(maxlen=self.max_events_per_stream)

        # 如果队列已满，移除最旧的事件
        if len(self.streams[stream_id]) == self.max_events_per_stream:
            oldest_event = self.streams[stream_id][0]
            self.event_index.pop(oldest_event.event_id, None)

        # 添加新事件
        self.streams[stream_id].append(event_entry)
        self.event_index[event_id] = event_entry

        logger.debug(f"存储事件 {event_id} 到流 {stream_id}")
        return event_id

    async def replay_events_after(
        self,
        last_event_id: EventId,
        send_callback: EventCallback,
    ) -> StreamId | None:
        """重放指定事件ID之后的事件"""
        if last_event_id not in self.event_index:
            logger.warning(f"事件ID {last_event_id} 未找到")
            return None

        # 获取流并找到指定事件之后的事件
        last_event = self.event_index[last_event_id]
        stream_id = last_event.stream_id
        stream_events = self.streams.get(last_event.stream_id, deque())

        # 事件按时间顺序排列，找到指定事件后的所有事件
        found_last = False
        replayed_count = 0
        for event in stream_events:
            if found_last:
                await send_callback(EventMessage(event.message, event.event_id))
                replayed_count += 1
            elif event.event_id == last_event_id:
                found_last = True

        logger.info(f"重放了 {replayed_count} 个事件到流 {stream_id}")
        return stream_id
