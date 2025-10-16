"""
核心检查逻辑单元测试
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from checker import DXFParser, ComplianceChecker


def test_parser():
    """测试 DXF 解析器"""
    print("测试 DXF 解析器...")
    
    # 查找测试文件
    test_files = list(Path('.').glob('*.dxf'))
    if not test_files:
        print("  ⚠️  未找到测试 DXF 文件，跳过解析测试")
        return False
    
    test_file = test_files[0]
    print(f"  使用测试文件: {test_file}")
    
    try:
        parser = DXFParser()
        data = parser.parse(str(test_file))
        
        print(f"  ✓ 文件名: {data['filename']}")
        print(f"  ✓ DXF 版本: {data['version']}")
        print(f"  ✓ 图层数量: {len(data['layers'])}")
        print(f"  ✓ 实体数量: {data['metadata']['entity_count']}")
        print(f"  ✓ 文字数量: {len(data['texts'])}")
        print(f"  ✓ 尺寸数量: {len(data['dimensions'])}")
        
        return True
    except Exception as e:
        print(f"  ✗ 解析失败: {e}")
        return False


def test_checker():
    """测试合规性检查器"""
    print("\n测试合规性检查器...")
    
    # 查找测试文件
    test_files = list(Path('.').glob('*.dxf'))
    if not test_files:
        print("  ⚠️  未找到测试 DXF 文件，跳过检查测试")
        return False
    
    test_file = test_files[0]
    
    try:
        # 解析文件
        parser = DXFParser()
        data = parser.parse(str(test_file))
        
        # 执行检查
        checker = ComplianceChecker()
        report = checker.check(data, "test-analysis", "test-file")
        
        print(f"  ✓ 分析ID: {report.analysis_id}")
        print(f"  ✓ 标准: {report.standard}")
        print(f"  ✓ 总违规数: {report.total_violations}")
        print(f"  ✓ 严重错误: {report.critical_count}")
        print(f"  ✓ 警告: {report.warning_count}")
        print(f"  ✓ 提示: {report.info_count}")
        print(f"  ✓ 合规得分: {report.compliance_score:.1f}")
        print(f"  ✓ 是否合规: {'是' if report.is_compliant else '否'}")
        
        if report.violations:
            print(f"\n  前3个违规项:")
            for i, v in enumerate(report.violations[:3], 1):
                print(f"    {i}. [{v.severity}] {v.type}: {v.description[:50]}...")
        
        return True
    except Exception as e:
        print(f"  ✗ 检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rules_config():
    """测试规则配置加载"""
    print("\n测试规则配置加载...")
    
    try:
        checker = ComplianceChecker()
        rules = checker.rules
        
        print(f"  ✓ 加载规则配置成功")
        print(f"  ✓ 标准名称: {rules['standard']['name']}")
        print(f"  ✓ 图层规则: {len(rules['layers'])} 个")
        print(f"  ✓ 线宽规则: 粗线 {rules['lineweights']['thick_line']}mm")
        print(f"  ✓ 字体规则: 最小高度 {rules['fonts']['min_height']}mm")
        print(f"  ✓ 尺寸规则: 一致性阈值 {rules['dimensions']['consistency_threshold']*100}%")
        
        return True
    except Exception as e:
        print(f"  ✗ 配置加载失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("CAD 规范符合性检查器 - 核心功能测试")
    print("=" * 60)
    
    results = []
    
    # 测试规则配置
    results.append(test_rules_config())
    
    # 测试解析器
    results.append(test_parser())
    
    # 测试检查器
    results.append(test_checker())
    
    # 汇总结果
    print("\n" + "=" * 60)
    print(f"测试完成: {sum(results)}/{len(results)} 通过")
    print("=" * 60)
    
    if all(results):
        print("\n✅ 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
