"""
DWG 转换功能测试脚本

使用方法:
python test_dwg_converter.py path/to/your/file.dwg
"""
import sys
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.dwg_converter import DWGConverterService
from app.config import settings


async def test_dwg_conversion(dwg_file_path: str):
    """测试 DWG 文件转换"""
    
    print("=" * 60)
    print("DWG 转换测试")
    print("=" * 60)
    
    dwg_path = Path(dwg_file_path)
    
    # 检查文件是否存在
    if not dwg_path.exists():
        print(f"❌ 错误: 文件不存在: {dwg_file_path}")
        return
    
    if dwg_path.suffix.lower() != '.dwg':
        print(f"❌ 错误: 不是 DWG 文件: {dwg_file_path}")
        return
    
    print(f"\n📁 输入文件: {dwg_path.name}")
    print(f"📏 文件大小: {dwg_path.stat().st_size / 1024:.2f} KB")
    
    # 初始化转换器
    converter = DWGConverterService()
    
    print("\n🔄 开始转换...")
    print("-" * 60)
    
    try:
        # 尝试转换
        dxf_path = await converter.convert_to_dxf(str(dwg_path))
        
        print(f"\n✅ 转换成功!")
        print(f"📄 输出文件: {Path(dxf_path).name}")
        print(f"📏 输出大小: {Path(dxf_path).stat().st_size / 1024:.2f} KB")
        print(f"📍 完整路径: {dxf_path}")
        
        # 验证 DXF 文件
        print("\n🔍 验证 DXF 文件...")
        try:
            import ezdxf
            doc = ezdxf.readfile(dxf_path)
            print(f"✅ DXF 版本: {doc.dxfversion}")
            print(f"✅ 图层数量: {len(list(doc.layers))}")
            print(f"✅ 实体数量: {len(list(doc.modelspace()))}")
        except Exception as e:
            print(f"⚠️  验证警告: {str(e)}")
        
    except ValueError as e:
        print(f"\n❌ 转换失败:")
        print(str(e))
        print("\n💡 解决建议:")
        print("1. 安装 ODA File Converter:")
        print("   https://www.opendesign.com/guestfiles/oda_file_converter")
        print("2. 在 .env 文件中配置路径:")
        print("   ODA_CONVERTER_PATH=C:/Program Files/ODA/ODAFileConverter/ODAFileConverter.exe")
        print("3. 或在 AutoCAD 中手动转换为 DXF")
    
    except Exception as e:
        print(f"\n❌ 未知错误: {str(e)}")
    
    finally:
        print("\n" + "=" * 60)


def print_config():
    """打印当前配置"""
    print("\n📋 当前配置:")
    print(f"  - 上传目录: {settings.upload_dir}")
    print(f"  - 临时目录: {settings.temp_dir}")
    print(f"  - ODA 路径: {settings.oda_converter_path or '(未配置)'}")
    print(f"  - 允许格式: {', '.join(settings.allowed_extensions)}")
    print(f"  - 最大大小: {settings.max_upload_size / (1024*1024):.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法:")
        print(f"  python {Path(__file__).name} <dwg文件路径>")
        print("\n示例:")
        print(f"  python {Path(__file__).name} E:/drawings/sample.dwg")
        print_config()
        sys.exit(1)
    
    dwg_file = sys.argv[1]
    
    # 运行测试
    asyncio.run(test_dwg_conversion(dwg_file))
