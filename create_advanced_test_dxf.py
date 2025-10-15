#!/usr/bin/env python3
"""
创建更复杂的测试 DXF 文件
包含更多种类的图元和违规项
"""
import ezdxf
from pathlib import Path

def create_advanced_test_dxf():
    """创建一个包含更复杂测试数据的 DXF 文件"""
    
    # 创建新的 DXF 文档（AutoCAD 2018）
    doc = ezdxf.new('R2018', setup=True)
    msp = doc.modelspace()
    
    # 创建更多图层
    doc.layers.new('OUTLINE', dxfattribs={'color': 1, 'lineweight': 50})  # 粗线
    doc.layers.new('DIMENSION', dxfattribs={'color': 3, 'lineweight': 25})  # 尺寸
    doc.layers.new('TEXT', dxfattribs={'color': 2, 'lineweight': 18})  # 文字
    doc.layers.new('CENTERLINE', dxfattribs={'color': 4, 'lineweight': 13, 'linetype': 'CENTER'})
    doc.layers.new('HIDDEN', dxfattribs={'color': 8, 'lineweight': 25, 'linetype': 'HIDDEN'})
    doc.layers.new('SECTION', dxfattribs={'color': 5, 'lineweight': 35})
    doc.layers.new('DETAIL', dxfattribs={'color': 6, 'lineweight': 30})
    
    # ============= 正确的图元示例 =============
    
    # 1. 主视图外轮廓（正确图层）
    outline_points = [
        (0, 0), (150, 0), (150, 100), (120, 120), (30, 120), (0, 100), (0, 0)
    ]
    for i in range(len(outline_points) - 1):
        msp.add_line(
            outline_points[i], outline_points[i + 1],
            dxfattribs={'layer': 'OUTLINE'}
        )
    
    # 2. 内部特征线（正确图层）
    msp.add_circle((75, 50), 15, dxfattribs={'layer': 'OUTLINE'})
    msp.add_circle((75, 50), 25, dxfattribs={'layer': 'OUTLINE'})
    msp.add_arc((75, 50), 35, 45, 135, dxfattribs={'layer': 'OUTLINE'})
    
    # 3. 中心线（正确图层和线型）
    msp.add_line((75, -10), (75, 130), dxfattribs={'layer': 'CENTERLINE'})
    msp.add_line((-10, 50), (160, 50), dxfattribs={'layer': 'CENTERLINE'})
    
    # 4. 隐藏线（正确图层和线型）
    msp.add_line((30, 30), (120, 30), dxfattribs={'layer': 'HIDDEN'})
    msp.add_line((30, 70), (120, 70), dxfattribs={'layer': 'HIDDEN'})
    
    # 5. 正确的尺寸标注
    msp.add_linear_dim(
        base=(75, -20),
        p1=(0, 0), p2=(150, 0),
        dimstyle='EZDXF',
        dxfattribs={'layer': 'DIMENSION'}
    )
    
    msp.add_linear_dim(
        base=(-20, 50),
        p1=(0, 0), p2=(0, 100),
        dimstyle='EZDXF',
        dxfattribs={'layer': 'DIMENSION', 'angle': 90}
    )
    
    # 6. 正确的文字标注
    msp.add_text(
        '主视图',
        dxfattribs={
            'layer': 'TEXT',
            'height': 5,  # 符合规范
            'insert': (75, 140),
            'halign': 1  # 居中
        }
    )
    
    msp.add_text(
        '比例 1:1',
        dxfattribs={
            'layer': 'TEXT',
            'height': 3.5,  # 符合规范
            'insert': (140, 140)
        }
    )
    
    msp.add_mtext(
        '材料: Q235钢\n表面处理: 喷漆\n技术要求:\n1. 焊接按 GB/T 5117\n2. 尺寸未注公差 ±0.5',
        dxfattribs={
            'layer': 'TEXT',
            'char_height': 2.5,  # 符合规范
            'insert': (160, 100),
            'width': 60
        }
    )
    
    # ============= 故意的违规项 =============
    
    # 违规1: 尺寸标注在错误图层
    msp.add_linear_dim(
        base=(75, 110),
        p1=(30, 120), p2=(120, 120),
        dimstyle='EZDXF',
        dxfattribs={'layer': '0'}  # ❌ 错误：应在 DIMENSION 层
    )
    
    # 违规2: 多个文字高度问题
    # 2a. 文字过小
    msp.add_text(
        '过小标注',
        dxfattribs={
            'layer': 'TEXT',
            'height': 1.2,  # ❌ 错误：小于 2.5mm
            'insert': (10, 140)
        }
    )
    
    # 2b. 文字过大
    msp.add_text(
        '过大',
        dxfattribs={
            'layer': 'TEXT',
            'height': 15,  # ❌ 错误：大于 10mm
            'insert': (10, 120)
        }
    )
    
    # 2c. MTEXT 高度过小
    msp.add_mtext(
        '这是过小的多行文字\n第二行内容',
        dxfattribs={
            'layer': 'TEXT',
            'char_height': 1.8,  # ❌ 错误：小于 2.5mm
            'insert': (160, 40),
            'width': 40
        }
    )
    
    # 违规3: 文字在错误图层
    msp.add_text(
        '错误图层文字',
        dxfattribs={
            'layer': 'OUTLINE',  # ❌ 错误：应在 TEXT 层
            'height': 4,
            'insert': (160, 20)
        }
    )
    
    # 违规4: 使用非标准线宽
    # 4a. 过粗线宽
    msp.add_line(
        (170, 0), (170, 100),
        dxfattribs={
            'layer': 'OUTLINE',
            'lineweight': 100  # ❌ 错误：1.0mm 非标准
        }
    )
    
    # 4b. 过细线宽
    msp.add_line(
        (175, 0), (175, 100),
        dxfattribs={
            'layer': 'OUTLINE',
            'lineweight': 15   # ❌ 错误：0.15mm 过细
        }
    )
    
    # 4c. 奇怪的线宽
    msp.add_line(
        (180, 0), (180, 100),
        dxfattribs={
            'layer': 'OUTLINE',
            'lineweight': 42   # ❌ 错误：0.42mm 非标准
        }
    )
    
    # 违规5: 使用过多非标准颜色
    for i, color in enumerate([11, 12, 13, 14, 15, 16, 17, 18, 19, 20]):
        msp.add_circle(
            (200 + i * 10, 50), 3,
            dxfattribs={'layer': 'OUTLINE', 'color': color}  # ❌ 错误：使用花哨颜色
        )
    
    # 违规6: 尺寸标注不一致
    # 不同的箭头大小
    dim1 = msp.add_linear_dim(
        base=(220, 20),
        p1=(200, 0), p2=(250, 0),
        dimstyle='EZDXF',
        dxfattribs={'layer': 'DIMENSION'}
    )
    
    dim2 = msp.add_linear_dim(
        base=(220, 80),
        p1=(200, 60), p2=(250, 60),
        dimstyle='EZDXF2',  # 不同的样式会导致不一致
        dxfattribs={'layer': 'DIMENSION'}
    )
    
    # 创建第二个视图区域
    # ============= 左视图（更多测试数据）=============
    
    # 左视图轮廓
    left_view_points = [
        (300, 0), (350, 0), (350, 100), (300, 100), (300, 0)
    ]
    for i in range(len(left_view_points) - 1):
        msp.add_line(
            left_view_points[i], left_view_points[i + 1],
            dxfattribs={'layer': 'OUTLINE'}
        )
    
    # 剖面线（正确）
    for y in range(10, 91, 10):
        msp.add_line(
            (305, y), (345, y - 5),
            dxfattribs={'layer': 'SECTION'}
        )
    
    # 左视图标题
    msp.add_text(
        '左视图',
        dxfattribs={
            'layer': 'TEXT',
            'height': 5,
            'insert': (325, 110),
            'halign': 1
        }
    )
    
    # ============= 详细视图标记 =============
    
    # 详细视图圆圈
    msp.add_circle((400, 50), 20, dxfattribs={'layer': 'DETAIL'})
    msp.add_text(
        'A',
        dxfattribs={
            'layer': 'DETAIL',
            'height': 8,
            'insert': (400, 50),
            'halign': 1,
            'valign': 2
        }
    )
    
    # 比例标注
    msp.add_text(
        '详图 A (2:1)',
        dxfattribs={
            'layer': 'TEXT',
            'height': 4,
            'insert': (400, 20)
        }
    )
    
    # 保存文件
    output_dir = Path(__file__).parent / "backend" / "uploads"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = output_dir / "advanced_test_sample.dxf"
    doc.saveas(test_file)
    
    print(f"✅ 高级测试 DXF 文件已创建: {test_file}")
    print()
    print("📊 文件内容:")
    print(f"   - 图层数: {len(list(doc.layers))}")
    print(f"   - 实体数: {len(list(msp))}")
    print()
    print("预期检查结果:")
    print("   ✅ 符合规范的项目:")
    print("      - 正确图层使用")
    print("      - 标准线宽")
    print("      - 合适的文字高度")
    print("      - 正确的尺寸标注位置")
    print()
    print("   ❌ 违规项 (预计 10+ 个):")
    print("      1. 尺寸标注在错误图层 (1个)")
    print("      2. 文字高度过小 (2个)")
    print("      3. 文字高度过大 (1个)")
    print("      4. 文字在错误图层 (1个)")
    print("      5. 使用非标准线宽 (3个)")
    print("      6. 使用过多非标准颜色 (10个圆圈)")
    print("      7. 尺寸标注样式不一致")
    print()
    print("使用方法:")
    print(f"   1. 访问 http://localhost:3000")
    print(f"   2. 上传文件: {test_file.name}")
    print(f"   3. 查看详细分析报告")
    
    return test_file


if __name__ == "__main__":
    create_advanced_test_dxf()