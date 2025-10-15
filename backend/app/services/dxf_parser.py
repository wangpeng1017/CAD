"""
DXF 文件解析服务
"""
import ezdxf
from pathlib import Path
from typing import Dict, List, Any


class DXFParserService:
    """DXF 文件解析器"""
    
    def __init__(self):
        self.doc = None
        self.modelspace = None
        
    async def parse(self, file_path: str) -> Dict[str, Any]:
        """
        解析 DXF 文件
        
        Args:
            file_path: DXF 文件路径
            
        Returns:
            解析后的数据结构
        """
        try:
            # 读取 DXF 文件
            self.doc = ezdxf.readfile(file_path)
            self.modelspace = self.doc.modelspace()
            
            # 提取关键信息
            data = {
                "filename": Path(file_path).name,
                "version": self.doc.dxfversion,
                "layers": self._extract_layers(),
                "entities": self._extract_entities(),
                "dimensions": self._extract_dimensions(),
                "texts": self._extract_texts(),
                "blocks": self._extract_blocks(),
                "metadata": self._extract_metadata()
            }
            
            return data
            
        except ezdxf.DXFError as e:
            raise ValueError(f"DXF 文件解析失败: {str(e)}")
        except Exception as e:
            raise ValueError(f"文件处理错误: {str(e)}")
    
    def _extract_layers(self) -> List[Dict[str, Any]]:
        """提取图层信息"""
        layers = []
        for layer in self.doc.layers:
            layers.append({
                "name": layer.dxf.name,
                "color": layer.dxf.color,
                "linetype": layer.dxf.linetype,
                "lineweight": getattr(layer.dxf, 'lineweight', -1),
                "is_locked": layer.is_locked(),
                "is_off": layer.is_off()
            })
        return layers
    
    def _extract_entities(self) -> Dict[str, List[Dict[str, Any]]]:
        """提取所有图元信息"""
        entities = {
            "LINE": [],
            "CIRCLE": [],
            "ARC": [],
            "POLYLINE": [],
            "TEXT": [],
            "MTEXT": [],
            "DIMENSION": [],
            "OTHER": []
        }
        
        for entity in self.modelspace:
            entity_type = entity.dxftype()
            entity_data = {
                "handle": entity.dxf.handle,
                "layer": entity.dxf.layer,
                "color": entity.dxf.color,
                "linetype": entity.dxf.linetype,
                "lineweight": getattr(entity.dxf, 'lineweight', -1)
            }
            
            # 根据类型提取特定信息
            if entity_type == "LINE":
                entity_data.update({
                    "start": (entity.dxf.start.x, entity.dxf.start.y),
                    "end": (entity.dxf.end.x, entity.dxf.end.y)
                })
                entities["LINE"].append(entity_data)
                
            elif entity_type == "CIRCLE":
                entity_data.update({
                    "center": (entity.dxf.center.x, entity.dxf.center.y),
                    "radius": entity.dxf.radius
                })
                entities["CIRCLE"].append(entity_data)
                
            elif entity_type in ["TEXT", "MTEXT"]:
                # TEXT 和 MTEXT 的高度属性不同
                if entity_type == "TEXT":
                    height = entity.dxf.height
                    text_content = entity.dxf.text
                else:  # MTEXT
                    height = getattr(entity.dxf, 'char_height', 2.5)
                    text_content = entity.text
                
                entity_data.update({
                    "text": text_content,
                    "height": height,
                    "position": (entity.dxf.insert.x, entity.dxf.insert.y)
                })
                entities["TEXT" if entity_type == "TEXT" else "MTEXT"].append(entity_data)
                
            elif entity_type.startswith("DIMENSION"):
                entities["DIMENSION"].append(entity_data)
                
            else:
                entities["OTHER"].append(entity_data)
        
        return entities
    
    def _extract_dimensions(self) -> List[Dict[str, Any]]:
        """提取尺寸标注信息"""
        dimensions = []
        
        for dim in self.modelspace.query('DIMENSION'):
            dim_data = {
                "handle": dim.dxf.handle,
                "layer": dim.dxf.layer,
                "dimtype": dim.dxftype(),
                "text_override": getattr(dim.dxf, 'text', ''),
                "text_height": getattr(dim.dxf, 'dimtxt', 0),
                "arrow_size": getattr(dim.dxf, 'dimasz', 0),
                "color": dim.dxf.color
            }
            
            # 尝试获取尺寸界线和尺寸线信息
            try:
                measurement = dim.get_measurement()
                dim_data["measurement"] = measurement
            except:
                pass
            
            dimensions.append(dim_data)
        
        return dimensions
    
    def _extract_texts(self) -> List[Dict[str, Any]]:
        """提取所有文字信息"""
        texts = []
        
        for text_entity in self.modelspace.query('TEXT MTEXT'):
            # TEXT 和 MTEXT 的高度属性不同
            entity_type = text_entity.dxftype()
            if entity_type == "TEXT":
                height = text_entity.dxf.height
                text_content = text_entity.dxf.text
            else:  # MTEXT
                height = getattr(text_entity.dxf, 'char_height', 2.5)
                text_content = text_entity.text
            
            text_data = {
                "handle": text_entity.dxf.handle,
                "type": entity_type,
                "layer": text_entity.dxf.layer,
                "text": text_content,
                "height": height,
                "style": getattr(text_entity.dxf, 'style', 'Standard'),
                "color": text_entity.dxf.color
            }
            texts.append(text_data)
        
        return texts
    
    def _extract_blocks(self) -> List[str]:
        """提取块定义信息"""
        return [block.name for block in self.doc.blocks if not block.name.startswith('*')]
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """提取文件元数据"""
        header = self.doc.header
        metadata = {
            "dxf_version": self.doc.dxfversion,
            "units": getattr(header, '$INSUNITS', 0),
            "layer_count": len(list(self.doc.layers)),
            "entity_count": len(list(self.modelspace))
        }
        
        # 提取图纸范围
        try:
            metadata["extmin"] = tuple(header['$EXTMIN'])
            metadata["extmax"] = tuple(header['$EXTMAX'])
        except:
            pass
        
        return metadata
