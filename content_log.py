#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


LOG_FILE = Path("content_log.json")

CONTENT_TYPES = {
    "选题": "topic",
    "写作": "writing",
    "素材": "material",
    "发布": "publish",
    "复盘": "review",
}

VALID_STATUSES = ["想法", "进行中", "已完成", "已发布", "暂停"]


def load_logs():
    """读取日志文件"""
    if not LOG_FILE.exists():
        return []

    try:
        with LOG_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        print("日志文件格式不正确，将使用空日志。")
        return []

    except json.JSONDecodeError:
        print("日志文件不是有效的 JSON，将使用空日志。")
        return []


def save_logs(logs):
    """保存日志文件"""
    with LOG_FILE.open("w", encoding="utf-8") as file:
        json.dump(logs, file, ensure_ascii=False, indent=2)


def create_log(
    content_type,
    title,
    platform="",
    status="已完成",
    duration=0,
    tags="",
    notes="",
    log_date=None,
):
    """创建一条内容工作日志"""
    logs = load_logs()

    if content_type not in CONTENT_TYPES:
        print(f"类型必须是：{'、'.join(CONTENT_TYPES.keys())}")
        return

    if status not in VALID_STATUSES:
        print(f"状态必须是：{'、'.join(VALID_STATUSES)}")
        return

    if log_date is None:
        log_date = date.today().isoformat()

    tags_list = [
        tag.strip()
        for tag in tags.replace("，", ",").split(",")
        if tag.strip()
    ]

    log = {
        "id": len(logs) + 1,
        "date": log_date,
        "type": content_type,
        "title": title,
        "platform": platform,
        "status": status,
        "duration": float(duration),
        "tags": tags_list,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    logs.append(log)
    save_logs(logs)

    print("记录成功：")
    print_log(log)


def print_log(log):
    """格式化显示一条日志"""
    tags = "、".join(log.get("tags", [])) or "无"
    platform = log.get("platform") or "未指定"
    duration = log.get("duration", 0)

    print(
        f"[{log.get('date')}] "
        f"{log.get('type')} | "
        f"{log.get('title')} | "
        f"平台：{platform} | "
        f"状态：{log.get('status')} | "
        f"耗时：{duration} 小时 | "
        f"标签：{tags}"
    )

    if log.get("notes"):
        print(f"  备注：{log['notes']}")


def get_date_range(days):
    """获取日期范围"""
    today = date.today()
    start_date = today - timedelta(days=days - 1)
    return start_date.isoformat(), today.isoformat()


def filter_logs(logs, days=None, content_type=None, platform=None, status=None):
    """根据条件筛选日志"""
    if days is not None:
        start_date, end_date = get_date_range(days)
        logs = [
            log
            for log in logs
            if start_date <= log.get("date", "") <= end_date
        ]

    if content_type:
        logs = [log for log in logs if log.get("type") == content_type]

    if platform:
        logs = [
            log
            for log in logs
            if log.get("platform", "").lower() == platform.lower()
        ]

    if status:
        logs = [log for log in logs if log.get("status") == status]

    return sorted(
        logs,
        key=lambda item: (
            item.get("date", ""),
            item.get("created_at", ""),
        ),
        reverse=True,
    )


def list_logs(days=7, content_type=None, platform=None, status=None):
    """查看日志列表"""
    logs = load_logs()
    logs = filter_logs(
        logs,
        days=days,
        content_type=content_type,
        platform=platform,
        status=status,
    )

    if not logs:
        print("没有找到符合条件的记录。")
        return

    print(f"最近 {days} 天共有 {len(logs)} 条记录：\n")

    for log in logs:
        print_log(log)


def search_logs(keyword):
    """搜索日志"""
    logs = load_logs()
    keyword = keyword.lower()

    results = []

    for log in logs:
        searchable_text = " ".join(
            [
                str(log.get("type", "")),
                str(log.get("title", "")),
                str(log.get("platform", "")),
                str(log.get("status", "")),
                str(log.get("notes", "")),
                " ".join(log.get("tags", [])),
            ]
        ).lower()

        if keyword in searchable_text:
            results.append(log)

    if not results:
        print(f"没有找到与“{keyword}”相关的记录。")
        return

    print(f"找到 {len(results)} 条记录：\n")

    for log in sorted(results, key=lambda item: item.get("date", ""), reverse=True):
        print_log(log)


def print_statistics(logs):
    """输出统计信息"""
    total_duration = sum(float(log.get("duration", 0)) for log in logs)

    type_counter = Counter(log.get("type", "未分类") for log in logs)
    status_counter = Counter(log.get("status", "未分类") for log in logs)
    platform_counter = Counter(log.get("platform") or "未指定" for log in logs)

    print(f"记录数量：{len(logs)} 条")
    print(f"总投入时间：{total_duration:.1f} 小时")

    print("\n按工作类型：")
    for name, count in type_counter.most_common():
        print(f"- {name}：{count} 条")

    print("\n按状态：")
    for name, count in status_counter.most_common():
        print(f"- {name}：{count} 条")

    print("\n按平台：")
    for name, count in platform_counter.most_common():
        print(f"- {name}：{count} 条")


def summary(days=1):
    """生成日报或周报"""
    logs = load_logs()
    logs = filter_logs(logs, days=days)

    if not logs:
        print(f"最近 {days} 天没有内容工作记录。")
        return

    title = "日报" if days == 1 else f"最近 {days} 天内容工作总结"

    print("=" * 50)
    print(title)
    print("=" * 50)

    print_statistics(logs)

    print("\n详细记录：")
    for log in logs:
        print_log(log)

    completed_topics = [
        log
        for log in logs
        if log.get("type") == "选题"
        and log.get("status") in ["已完成", "已发布"]
    ]

    published_items = [
        log
        for log in logs
        if log.get("type") == "发布"
        or log.get("status") == "已发布"
    ]

    print("\n创作进度：")
    print(f"- 已完成选题：{len(completed_topics)} 个")
    print(f"- 发布内容：{len(published_items)} 个")


def show_pipeline():
    """查看当前内容生产流水线"""
    logs = load_logs()

    print("=" * 50)
    print("当前内容生产流水线")
    print("=" * 50)

    for content_type in CONTENT_TYPES:
        type_logs = [
            log
            for log in logs
            if log.get("type") == content_type
            and log.get("status") in ["想法", "进行中"]
        ]

        print(f"\n【{content_type}】")

        if not type_logs:
            print("暂无进行中的内容")
            continue

        for log in sorted(
            type_logs,
            key=lambda item: item.get("date", ""),
            reverse=True,
        ):
            print_log(log)


def build_parser():
    """构建命令行参数"""
    parser = argparse.ArgumentParser(description="AI 内容创作者工作日志记录器")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="新增一条内容工作记录")
    add_parser.add_argument(
        "--type",
        required=True,
        choices=list(CONTENT_TYPES.keys()),
        help="工作类型：选题、写作、素材、发布、复盘",
    )
    add_parser.add_argument("--title", required=True, help="标题或工作内容")
    add_parser.add_argument("--platform", default="", help="平台")
    add_parser.add_argument("--status", default="已完成", choices=VALID_STATUSES, help="状态")
    add_parser.add_argument("--duration", type=float, default=0, help="耗时，单位为小时")
    add_parser.add_argument("--tags", default="", help="标签，多个标签用逗号分隔")
    add_parser.add_argument("--notes", default="", help="备注")
    add_parser.add_argument("--date", default=None, help="日期，格式为 YYYY-MM-DD，默认今天")

    list_parser = subparsers.add_parser("list", help="查看内容工作记录")
    list_parser.add_argument("--days", type=int, default=7, help="查看最近多少天，默认 7 天")
    list_parser.add_argument("--type", choices=list(CONTENT_TYPES.keys()), help="按工作类型筛选")
    list_parser.add_argument("--platform", help="按平台筛选")
    list_parser.add_argument("--status", choices=VALID_STATUSES, help="按状态筛选")

    search_parser = subparsers.add_parser("search", help="搜索内容工作记录")
    search_parser.add_argument("--keyword", required=True, help="搜索关键词")

    summary_parser = subparsers.add_parser("summary", help="生成日报或周报")
    summary_parser.add_argument("--days", type=int, default=1, help="统计最近多少天，默认 1 天")

    subparsers.add_parser("pipeline", help="查看正在进行中的内容流水线")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "add":
        create_log(
            content_type=args.type,
            title=args.title,
            platform=args.platform,
            status=args.status,
            duration=args.duration,
            tags=args.tags,
            notes=args.notes,
            log_date=args.date,
        )
    elif args.command == "list":
        list_logs(
            days=args.days,
            content_type=args.type,
            platform=args.platform,
            status=args.status,
        )
    elif args.command == "search":
        search_logs(args.keyword)
    elif args.command == "summary":
        summary(days=args.days)
    elif args.command == "pipeline":
        show_pipeline()


if __name__ == "__main__":
    main()
