#!/usr/bin/env python3
"""
创建测试用的 DXF 文件
包含多种图元和一些故意的规范违规项用于测试
"""
import ezdxf
from pathlib import Path

def create_test_dxf():
    """创建一个包含测试数据的 DXF 文件"""
    
    # 创建新的 DXF 文档（AutoCAD 2018）
    doc = ezdxf.new('R2018', setup=True)
    msp = doc.modelspace()
    
    # 创建图层（图层 '0' 已经存在，不需要创建）
    doc.layers.new('OUTLINE', dxfattribs={'color': 1, 'lineweight': 50})  # 轮廓层（粗线）
    doc.layers.new('DIMENSION', dxfattribs={'color': 3, 'lineweight': 25})  # 尺寸层
    doc.layers.new('TEXT', dxfattribs={'color': 2, 'lineweight': 18})  # 文字层
    doc.layers.new('CENTERLINE', dxfattribs={'color': 4, 'lineweight': 13, 'linetype': 'CENTER'})  # 中心线
    
    # ============= 添加测试图元 =============
    
    # 1. 在正确图层上的轮廓线
    msp.add_line((0, 0), (100, 0), dxfattribs={'layer': 'OUTLINE'})
    msp.add_line((100, 0), (100, 80), dxfattribs={'layer': 'OUTLINE'})
    msp.add_line((100, 80), (0, 80), dxfattribs={'layer': 'OUTLINE'})
    msp.add_line((0, 80), (0, 0), dxfattribs={'layer': 'OUTLINE'})
    
    # 2. 圆和圆弧
    msp.add_circle((50, 40), 15, dxfattribs={'layer': 'OUTLINE'})
    msp.add_arc((50, 40), 20, 0, 180, dxfattribs={'layer': 'OUTLINE'})
    
    # 3. 在正确图层上的尺寸标注
    dim = msp.add_linear_dim(
        base=(50, -10),
        p1=(0, 0),
        p2=(100, 0),
        dimstyle='EZDXF',
        dxfattribs={'layer': 'DIMENSION'}
    )
    
    # 4. 在正确图层上的文字
    msp.add_text(
        '测试图纸',
        dxfattribs={
            'layer': 'TEXT',
            'height': 5,  # 符合规范的文字高度
            'insert': (10, 90),
            'style': 'Standard'
        }
    )
    
    # 5. 在正确图层上的多行文字
    msp.add_mtext(
        'GB/T 14665-2012\n合规性测试图纸',
        dxfattribs={
            'layer': 'TEXT',
            'char_height': 3.5,
            'insert': (10, 70),
            'width': 80
        }
    )
    
    # ============= 添加故意的违规项用于测试 =============
    
    # 违规1: 尺寸标注在错误图层（应该在 DIMENSION 层）
    msp.add_linear_dim(
        base=(50, 85),
        p1=(0, 80),
        p2=(100, 80),
        dimstyle='EZDXF',
        dxfattribs={'layer': '0'}  # ❌ 错误：应该在 DIMENSION 层
    )
    
    # 违规2: 文字高度过小
    msp.add_text(
        '过小文字',
        dxfattribs={
            'layer': 'TEXT',
            'height': 1.5,  # ❌ 错误：小于最小高度 2.5mm
            'insert': (110, 50)
        }
    )
    
    # 违规3: 文字高度过大
    msp.add_text(
        '过大',
        dxfattribs={
            'layer': 'TEXT',
            'height': 12,  # ❌ 错误：大于最大高度 10mm
            'insert': (110, 30)
        }
    )
    
    # 违规4: 文字在错误图层
    msp.add_text(
        '错误图层的文字',
        dxfattribs={
            'layer': 'OUTLINE',  # ❌ 错误：应该在 TEXT 层
            'height': 4,
            'insert': (110, 70)
        }
    )
    
    # 违规5: 使用非标准线宽
    msp.add_line(
        (120, 0), (120, 80),
        dxfattribs={
            'layer': 'OUTLINE',
            'lineweight': 75  # ❌ 错误：非标准线宽（0.75mm）
        }
    )
    
    # 保存文件
    output_dir = Path(__file__).parent / "backend" / "uploads"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = output_dir / "test_sample.dxf"
    doc.saveas(test_file)
    
    print(f"✅ 测试 DXF 文件已创建: {test_file}")
    print()
    print("📊 文件内容:")
    print(f"   - 图层数: {len(list(doc.layers))}")
    print(f"   - 实体数: {len(list(msp))}")
    print()
    print("预期检查结果:")
    print("   ✅ 5 个符合规范的项目")
    print("   ❌ 5 个违规项：")
    print("      1. 尺寸标注在错误图层")
    print("      2. 文字高度过小 (1.5mm)")
    print("      3. 文字高度过大 (12mm)")
    print("      4. 文字在错误图层")
    print("      5. 使用非标准线宽 (0.75mm)")
    print()
    print("使用方法:")
    print(f"   1. 访问 http://localhost:3000")
    print(f"   2. 上传文件: {test_file.name}")
    print(f"   3. 查看分析报告")
    
    return test_file


if __name__ == "__main__":
    create_test_dxf()
