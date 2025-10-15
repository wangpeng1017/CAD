#!/usr/bin/env python3
"""
调试分析错误的脚本
"""
import sys
import asyncio
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.dxf_parser import DXFParserService
from app.services.compliance_checker import ComplianceCheckerService


async def debug_analysis(file_path: str):
    """调试分析流程"""
    print(f"=" * 60)
    print(f"调试分析流程: {file_path}")
    print(f"=" * 60)
    print()
    
    try:
        # Step 1: 检查文件是否存在
        print("Step 1: 检查文件...")
        if not Path(file_path).exists():
            print(f"❌ 文件不存在: {file_path}")
            return
        print(f"✅ 文件存在: {Path(file_path).name}")
        print()
        
        # Step 2: 解析 DXF
        print("Step 2: 解析 DXF 文件...")
        parser = DXFParserService()
        dxf_data = await parser.parse(file_path)
        print(f"✅ 解析成功!")
        print(f"   - DXF 版本: {dxf_data['version']}")
        print(f"   - 图层数: {len(dxf_data['layers'])}")
        print(f"   - 实体数: {sum(len(entities) for entities in dxf_data['entities'].values())}")
        print(f"   - 尺寸标注: {len(dxf_data['dimensions'])}")
        print(f"   - 文字: {len(dxf_data['texts'])}")
        print()
        
        # Step 3: 执行合规检查
        print("Step 3: 执行合规性检查...")
        checker = ComplianceCheckerService("GB/T 14665-2012")
        report = await checker.check(dxf_data, "test-analysis", file_path)
        print(f"✅ 检查完成!")
        print()
        
        # Step 4: 显示报告摘要
        print("=" * 60)
        print("合规性报告摘要")
        print("=" * 60)
        print(f"文件名: {report.filename}")
        print(f"标准: {report.standard}")
        print(f"合规得分: {report.compliance_score:.1f}")
        print(f"是否合规: {'✅ 是' if report.is_compliant else '❌ 否'}")
        print()
        print(f"违规统计:")
        print(f"  - 严重错误: {report.critical_count}")
        print(f"  - 警告: {report.warning_count}")
        print(f"  - 提示: {report.info_count}")
        print(f"  - 总计: {report.total_violations}")
        print()
        
        if report.violations:
            print("前 5 个违规项:")
            for i, violation in enumerate(report.violations[:5], 1):
                print(f"\n{i}. [{violation.severity.value}] {violation.type.value}")
                print(f"   规则: {violation.rule}")
                print(f"   描述: {violation.description}")
                if violation.suggestion:
                    print(f"   建议: {violation.suggestion}")
        
        print()
        print("=" * 60)
        print("✅ 调试完成 - 分析流程正常!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 错误发生:")
        print(f"   类型: {type(e).__name__}")
        print(f"   信息: {str(e)}")
        print()
        import traceback
        print("完整堆栈跟踪:")
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 查找最近上传的文件
        uploads_dir = Path(__file__).parent / "backend" / "uploads"
        if not uploads_dir.exists():
            print(f"❌ 上传目录不存在: {uploads_dir}")
            sys.exit(1)
        
        files = list(uploads_dir.glob("*.*"))
        if not files:
            print(f"❌ 上传目录中没有文件: {uploads_dir}")
            sys.exit(1)
        
        # 获取最新的文件
        file_path = str(max(files, key=lambda p: p.stat().st_mtime))
        print(f"使用最新上传的文件: {Path(file_path).name}")
        print()
    
    asyncio.run(debug_analysis(file_path))
