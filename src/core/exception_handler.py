#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一异常处理机制
提供标准化的异常处理和错误报告
"""

import sys
import traceback
from functools import wraps
from typing import Any, Callable, Optional, Type, Union
from src.utils.logger import get_logger


class CollectorError(Exception):
    """收集器基础异常类"""

    def __init__(
        self,
        message: str,
        site_name: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.site_name = site_name
        self.original_error = original_error


class NetworkError(CollectorError):
    """网络相关异常"""

    pass


class ParseError(CollectorError):
    """解析相关异常"""

    pass


class ConfigError(CollectorError):
    """配置相关异常"""

    pass


class WorkflowError(CollectorError):
    """工作流相关异常"""

    pass


class ErrorHandler:
    """错误处理器"""

    def __init__(self, logger_name: str = "error_handler"):
        self.logger = get_logger(logger_name)

    def handle_exception(self, error: Exception, context: str = "") -> dict:
        """处理异常并返回标准化错误信息"""
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context,
            "traceback": traceback.format_exc() if self.logger.level <= 10 else None,
        }

        if isinstance(error, CollectorError):
            error_info.update(
                {
                    "site_name": error.site_name,
                    "original_error": str(error.original_error)
                    if error.original_error
                    else None,
                }
            )

        # 记录错误日志
        self.logger.error(f"异常处理 [{context}]: {error_info['message']}")
        if error_info["traceback"]:
            self.logger.debug(f"详细堆栈: {error_info['traceback']}")

        return error_info

    def safe_execute(
        self,
        func: Callable,
        *args,
        context: str = "",
        default: Any = None,
        reraise: bool = False,
        **kwargs,
    ) -> Any:
        """安全执行函数"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_info = self.handle_exception(e, context or func.__name__)

            if reraise:
                raise e

            return default

    def retry_execute(
        self,
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        context: str = "",
        default: Any = None,
        **kwargs,
    ) -> Any:
        """重试执行函数"""
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return func(**kwargs)
            except Exception as e:
                last_error = e

                if attempt < max_retries:
                    self.logger.warning(f"重试 {attempt + 1}/{max_retries}: {str(e)}")
                    import time

                    time.sleep(delay * (2**attempt))  # 指数退避
                else:
                    self.handle_exception(e, context)
                    return default

        return default


# 全局错误处理器实例
global_error_handler = ErrorHandler()


def handle_exceptions(context: str = "", default: Any = None, reraise: bool = False):
    """异常处理装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return global_error_handler.safe_execute(
                func,
                *args,
                context=context or func.__name__,
                default=default,
                reraise=reraise,
                **kwargs,
            )

        return wrapper

    return decorator


def retry_on_exception(
    max_retries: int = 3, delay: float = 1.0, context: str = "", default: Any = None
):
    """重试装饰器"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(**kwargs):
            return global_error_handler.retry_execute(
                func,
                max_retries=max_retries,
                delay=delay,
                context=context or func.__name__,
                default=default,
                **kwargs,
            )

        return wrapper

    return decorator


def safe_network_call(
    func: Callable, *args, timeout: float = 30.0, default: Any = None, **kwargs
) -> Any:
    """安全的网络调用"""
    import signal

    def timeout_handler(signum, frame):
        raise TimeoutError(f"网络调用超时: {timeout}秒")

    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

        result = func(*args, **kwargs)
        signal.alarm(0)  # 取消超时
        return result

    except TimeoutError as e:
        global_error_handler.handle_exception(e, f"网络超时: {func.__name__}")
        return default
    except Exception as e:
        global_error_handler.handle_exception(e, f"网络错误: {func.__name__}")
        return default
    finally:
        signal.alarm(0)


class ErrorReporter:
    """错误报告器"""

    def __init__(self):
        self.logger = get_logger("error_reporter")
        self.errors = []

    def add_error(self, error: Exception, context: str = ""):
        """添加错误到报告"""
        error_info = global_error_handler.handle_exception(error, context)
        self.errors.append(error_info)

    def get_summary(self) -> dict:
        """获取错误摘要"""
        if not self.errors:
            return {"total": 0, "by_type": {}, "by_context": {}}

        summary = {"total": len(self.errors), "by_type": {}, "by_context": {}}

        for error in self.errors:
            # 按类型统计
            error_type = error["type"]
            summary["by_type"][error_type] = summary["by_type"].get(error_type, 0) + 1

            # 按上下文统计
            context = error["context"] or "unknown"
            summary["by_context"][context] = summary["by_context"].get(context, 0) + 1

        return summary

    def clear(self):
        """清空错误记录"""
        self.errors.clear()

    def has_errors(self) -> bool:
        """是否有错误"""
        return len(self.errors) > 0

    def get_recent_errors(self, count: int = 10) -> list:
        """获取最近的错误"""
        return self.errors[-count:] if self.errors else []


# 全局错误报告器
error_reporter = ErrorReporter()


if __name__ == "__main__":
    # 测试异常处理
    @handle_exceptions(context="测试函数", default="测试失败")
    def test_function():
        raise ValueError("这是一个测试异常")

    @retry_on_exception(max_retries=2, context="重试测试")
    def test_retry():
        import random

        if random.random() > 0.5:
            raise ConnectionError("连接失败")
        return "成功"

    print("测试异常处理:")
    result1 = test_function()
    print(f"结果1: {result1}")

    result2 = test_retry()
    print(f"结果2: {result2}")

    print("错误摘要:")
    summary = error_reporter.get_summary()
    print(f"总错误数: {summary['total']}")
    print(f"按类型: {summary['by_type']}")
    print(f"按上下文: {summary['by_context']}")
