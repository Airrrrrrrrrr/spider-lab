"""Pydantic v2 统一采集数据标准模型（为路线 B 数据质量网关与语料清洗打底）。"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator


class CrawlRecord(BaseModel):
    """标准化单条采集记录模型，内置空白清洗与幂等去重指纹计算。"""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    source_id: str = Field(..., min_length=2, description="数据源唯一英文标识")
    item_id: str = Field(..., min_length=1, description="站点内原始业务主键或详情唯一标识")
    url: str = Field(..., min_length=8, description="原始详情页或接口 URL")
    title: str = Field(..., min_length=1, description="清洗后的标题")
    content: str = Field(default="", description="正文纯文本或核心摘要")
    publish_time: str | None = Field(default=None, description="发布时间字符串")
    attachments: list[str] = Field(default_factory=list, description="附件 URL 列表")
    raw_extra: dict[str, Any] = Field(default_factory=dict, description="站点扩展业务字段")
    crawled_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="采集入库 UTC 时间戳",
    )

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        """压缩标题内部多余换行与连续空白字符。"""
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("标题清洗后不能为空")
        return cleaned

    @computed_field  # type: ignore[prop-decorator]
    @property
    def dedup_fingerprint(self) -> str:
        """生成基于 source_id + item_id + title + content 的幂等变更检测指纹。"""
        raw = f"{self.source_id}|{self.item_id}|{self.title}|{self.content}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
