"""
DWG 到 DXF 转换服务
支持多种转换方式
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional
import shutil

from app.config import settings


class DWGConverterService:
    """DWG 文件转换器"""
    
    def __init__(self):
        self.temp_dir = settings.temp_dir
        self.oda_converter_path = settings.oda_converter_path
        
    async def convert_to_dxf(self, dwg_path: str) -> str:
        """
        将 DWG 文件转换为 DXF
        
        Args:
            dwg_path: DWG 文件路径
            
        Returns:
            转换后的 DXF 文件路径
            
        Raises:
            ValueError: 转换失败
        """
        dwg_file = Path(dwg_path)
        
        if not dwg_file.exists():
            raise ValueError(f"DWG 文件不存在: {dwg_path}")
        
        # 尝试多种转换方法
        dxf_path = None
        errors = []
        
        # 方法 1: 使用 ODA File Converter（推荐）
        if self.oda_converter_path and os.path.exists(self.oda_converter_path):
            try:
                dxf_path = await self._convert_with_oda(dwg_path)
                if dxf_path:
                    return dxf_path
            except Exception as e:
                errors.append(f"ODA Converter 失败: {str(e)}")
        
        # 方法 2: 使用 ezdxf 的 readfile (支持部分 DWG 版本)
        try:
            dxf_path = await self._convert_with_ezdxf(dwg_path)
            if dxf_path:
                return dxf_path
        except Exception as e:
            errors.append(f"ezdxf 直接读取失败: {str(e)}")
        
        # 方法 3: 使用 LibreDWG (如果安装了)
        try:
            dxf_path = await self._convert_with_libredwg(dwg_path)
            if dxf_path:
                return dxf_path
        except Exception as e:
            errors.append(f"LibreDWG 失败: {str(e)}")
        
        # 所有方法都失败
        error_msg = "无法转换 DWG 文件。请尝试以下解决方案：\n"
        error_msg += "1. 在 AutoCAD 中手动将文件另存为 DXF 格式\n"
        error_msg += "2. 安装 ODA File Converter (https://www.opendesign.com/guestfiles/oda_file_converter)\n"
        error_msg += "3. 使用 LibreDWG 工具\n\n"
        error_msg += "错误详情:\n" + "\n".join(errors)
        
        raise ValueError(error_msg)
    
    async def _convert_with_oda(self, dwg_path: str) -> Optional[str]:
        """
        使用 ODA File Converter 转换
        
        ODA File Converter 是 Autodesk 官方推荐的 DWG/DXF 转换工具
        下载地址: https://www.opendesign.com/guestfiles/oda_file_converter
        """
        dwg_file = Path(dwg_path)
        output_dir = self.temp_dir / f"oda_{dwg_file.stem}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # ODA File Converter 命令行参数
        # 格式: ODAFileConverter <input_folder> <output_folder> <output_version> <output_format> <recursive> <audit>
        cmd = [
            self.oda_converter_path,
            str(dwg_file.parent),  # 输入文件夹
            str(output_dir),        # 输出文件夹
            "ACAD2018",             # 输出版本 (AutoCAD 2018 DXF)
            "DXF",                  # 输出格式
            "0",                    # 不递归
            "1"                     # 执行审计
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            # 查找生成的 DXF 文件
            dxf_file = output_dir / f"{dwg_file.stem}.dxf"
            if dxf_file.exists():
                # 移动到上传目录
                final_path = settings.upload_dir / f"{dwg_file.stem}_converted.dxf"
                shutil.move(str(dxf_file), str(final_path))
                return str(final_path)
            
        except subprocess.TimeoutExpired:
            raise ValueError("ODA 转换超时")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"ODA 转换失败: {e.stderr}")
        except Exception as e:
            raise ValueError(f"ODA 转换错误: {str(e)}")
        finally:
            # 清理临时目录
            if output_dir.exists():
                shutil.rmtree(output_dir, ignore_errors=True)
        
        return None
    
    async def _convert_with_ezdxf(self, dwg_path: str) -> Optional[str]:
        """
        使用 ezdxf 直接读取 DWG（支持有限）
        
        注意：ezdxf 仅支持读取部分 DWG 版本
        """
        import ezdxf
        
        dwg_file = Path(dwg_path)
        
        try:
            # 尝试直接读取 DWG
            doc = ezdxf.readfile(dwg_path)
            
            # 转换为 DXF
            dxf_path = settings.upload_dir / f"{dwg_file.stem}_converted.dxf"
            doc.saveas(str(dxf_path))
            
            return str(dxf_path)
            
        except ezdxf.DXFVersionError:
            # 不支持的 DWG 版本
            return None
        except Exception as e:
            raise ValueError(f"ezdxf 读取失败: {str(e)}")
    
    async def _convert_with_libredwg(self, dwg_path: str) -> Optional[str]:
        """
        使用 LibreDWG 转换
        
        LibreDWG 是开源的 DWG 读写库
        安装: pip install libredwg (需要系统依赖)
        """
        dwg_file = Path(dwg_path)
        dxf_path = settings.upload_dir / f"{dwg_file.stem}_converted.dxf"
        
        # 使用 dwg2dxf 命令行工具
        cmd = ["dwg2dxf", "-y", "-o", str(dxf_path), str(dwg_path)]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=True
            )
            
            if dxf_path.exists():
                return str(dxf_path)
                
        except FileNotFoundError:
            # LibreDWG 未安装
            return None
        except subprocess.TimeoutExpired:
            raise ValueError("LibreDWG 转换超时")
        except subprocess.CalledProcessError as e:
            raise ValueError(f"LibreDWG 转换失败: {e.stderr}")
        
        return None
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        if self.temp_dir.exists():
            for item in self.temp_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)


# 全局转换器实例
dwg_converter = DWGConverterService()
