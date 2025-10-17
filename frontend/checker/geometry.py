"""
几何关系引擎 - Phase 2
使用 Shapely 进行二维几何关系计算
"""
import uuid
from typing import List, Dict, Any, Tuple
from shapely.geometry import LineString, box, Point
from shapely import distance

from .models import Violation, ViolationType, SeverityLevel


class GeometryEngine:
    """几何关系分析引擎"""
    
    def __init__(self):
        self.violations: List[Violation] = []
    
    def check_dimension_text_overlap(self, dimensions: List[Dict], texts: List[Dict]) -> List[Violation]:
        """
        检测尺寸线与文字边界框是否相交
        
        P2-F01 验收标准 #1
        """
        violations = []
        
        for dim in dimensions:
            # 尝试获取尺寸线的几何信息
            if 'geometry' not in dim:
                continue
            
            dim_line = self._create_dimension_line(dim)
            if not dim_line:
                continue
            
            # 检查与所有文字的碰撞
            for text in texts:
                if 'position' not in text or 'height' not in text:
                    continue
                
                # 创建文字边界框（估算宽度）
                text_box = self._create_text_bbox(text)
                
                if dim_line.intersects(text_box):
                    violations.append(Violation(
                        id=str(uuid.uuid4()),
                        type=ViolationType.GEOMETRY,
                        severity=SeverityLevel.WARNING,
                        rule="GB/T 14665-2012 - 尺寸线与文字不应相交",
                        description=f"尺寸线与文字 '{text.get('text', '')[:20]}...' 发生相交",
                        entity_handle=dim.get('handle'),
                        layer=dim.get('layer'),
                        suggestion="调整尺寸线或文字位置，避免遮挡"
                    ))
        
        return violations
    
    def check_dimension_extension_line_gap(self, dimensions: List[Dict]) -> List[Violation]:
        """
        检查尺寸线端点与尺寸界线之间的距离
        
        P2-F01 验收标准 #2
        """
        violations = []
        tolerance = 1.0  # 允许误差 1mm
        
        for dim in dimensions:
            if 'extension_lines' not in dim:
                continue
            
            # 简化实现：检查尺寸线是否在界线之间
            # 实际 DXF 尺寸实体结构复杂，此处为示例
            
            # TODO: 实现具体的界线-尺寸线距离计算
            pass
        
        return violations
    
    def check_dimension_alignment(self, dimensions: List[Dict]) -> List[Violation]:
        """
        检测垂直/水平对齐的尺寸组，验证文字对齐
        
        P2-F01 验收标准 #3
        """
        violations = []
        
        # 分组：按接近的 Y 坐标（水平对齐）或 X 坐标（垂直对齐）
        horizontal_groups = self._group_dimensions_by_alignment(dimensions, axis='horizontal')
        vertical_groups = self._group_dimensions_by_alignment(dimensions, axis='vertical')
        
        # 检查每组内的文字对齐
        for group in horizontal_groups + vertical_groups:
            if len(group) < 2:
                continue
            
            misaligned = self._check_group_text_alignment(group)
            if misaligned:
                violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.GEOMETRY,
                    severity=SeverityLevel.INFO,
                    rule="GB/T 14665-2012 - 尺寸文字应对齐",
                    description=f"检测到 {len(group)} 个尺寸标注未对齐",
                    suggestion="对齐同一行/列的尺寸文字，提高可读性"
                ))
        
        return violations
    
    def _create_dimension_line(self, dim: Dict) -> LineString:
        """根据尺寸标注创建线段（简化实现）"""
        # DXF 尺寸实体结构复杂，此处简化
        # 实际应解析 DIMENSION 实体的几何块
        return None
    
    def _create_text_bbox(self, text: Dict) -> box:
        """创建文字的边界框"""
        x, y = text['position']
        height = text['height']
        # 估算宽度（汉字约等宽，字母约 0.6 倍高度）
        text_content = text.get('text', '')
        width = len(text_content) * height * 0.8
        
        return box(x, y, x + width, y + height)
    
    def _group_dimensions_by_alignment(
        self, 
        dimensions: List[Dict], 
        axis: str = 'horizontal'
    ) -> List[List[Dict]]:
        """将尺寸按对齐方式分组"""
        groups = []
        tolerance = 5.0  # 5mm 容差
        
        # TODO: 实现具体的分组逻辑
        # 需要根据尺寸标注的位置信息分组
        
        return groups
    
    def _check_group_text_alignment(self, group: List[Dict]) -> bool:
        """检查一组尺寸的文字是否对齐"""
        # TODO: 检查文字位置、小数点对齐
        return False
