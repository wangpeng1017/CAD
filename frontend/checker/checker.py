"""
CAD 合规性检查器
"""
import yaml
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from collections import Counter

from .models import (
    ComplianceReport,
    Violation,
    ViolationType,
    SeverityLevel
)
from .geometry import GeometryEngine


class ComplianceChecker:
    """合规性检查器"""
    
    def __init__(self, standard: str = "GB/T 14665-2012"):
        self.standard = standard
        self.rules = self._load_rules()
        self.violations: List[Violation] = []
        self.geometry_engine = GeometryEngine()  # Phase 2: 几何引擎
        
    def _load_rules(self) -> Dict[str, Any]:
        """加载规则配置"""
        config_file = Path(__file__).parent.parent / "config" / "rules_gbt14665.yaml"
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def check(
        self,
        dxf_data: Dict[str, Any],
        analysis_id: str,
        file_id: str
    ) -> ComplianceReport:
        """
        执行完整的合规性检查
        
        Args:
            dxf_data: 解析后的 DXF 数据
            analysis_id: 分析任务ID
            file_id: 文件ID
            
        Returns:
            合规性报告
        """
        self.violations = []
        
        # 执行各项检查
        self._check_layers(dxf_data)
        self._check_lineweights(dxf_data)
        self._check_colors(dxf_data)
        self._check_fonts(dxf_data)
        self._check_dimensions(dxf_data)
        
        # Phase 2: 几何关系检查
        self._check_geometry_relations(dxf_data)
        
        # 生成报告
        report = self._generate_report(dxf_data, analysis_id, file_id)
        return report
    
    def _check_layers(self, dxf_data: Dict[str, Any]):
        """检查图层规范"""
        rules = self.rules['layers']
        entities = dxf_data['entities']
        
        # 检查尺寸标注是否在正确图层
        expected_dim_layers = rules['尺寸层']['expected_names']
        for dim in entities.get('DIMENSION', []):
            layer = dim['layer']
            if not any(exp_name.upper() in layer.upper() for exp_name in expected_dim_layers):
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.LAYER,
                    severity=SeverityLevel.WARNING,
                    rule="GB/T 14665-2012 表6 - 图层规则",
                    description=f"尺寸标注应位于专用图层（如：{', '.join(expected_dim_layers)}），当前位于: {layer}",
                    entity_handle=dim['handle'],
                    layer=layer,
                    suggestion=f"将尺寸标注移至 {expected_dim_layers[0]} 图层"
                ))
        
        # 检查文字是否在正确图层
        expected_text_layers = rules['文字层']['expected_names']
        for text in entities.get('TEXT', []) + entities.get('MTEXT', []):
            layer = text['layer']
            # 跳过尺寸标注的文字
            if 'DIM' in layer.upper() or '尺寸' in layer:
                continue
            if not any(exp_name.upper() in layer.upper() for exp_name in expected_text_layers):
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.LAYER,
                    severity=SeverityLevel.INFO,
                    rule="GB/T 14665-2012 表6 - 图层规则",
                    description=f"文字应位于专用图层（如：{', '.join(expected_text_layers)}），当前位于: {layer}",
                    entity_handle=text['handle'],
                    layer=layer,
                    suggestion=f"将文字移至 {expected_text_layers[0]} 图层"
                ))
    
    def _check_lineweights(self, dxf_data: Dict[str, Any]):
        """检查线宽规范"""
        rules = self.rules['lineweights']
        tolerance = rules['tolerance']
        
        # 标准线宽值
        standard_weights = [
            rules['thick_line'],
            rules['medium_line'],
            rules['thin_line']
        ]
        
        # 检查所有线条实体
        for entity_type in ['LINE', 'CIRCLE', 'ARC', 'POLYLINE']:
            for entity in dxf_data['entities'].get(entity_type, []):
                lineweight = entity.get('lineweight', -1)
                
                # -1 表示使用默认值（ByLayer），-2 表示 ByBlock
                if lineweight < 0:
                    continue
                
                # 转换为 mm（DXF 中线宽单位是 1/100 mm）
                lineweight_mm = lineweight / 100.0
                
                # 检查是否符合标准线宽
                is_standard = any(
                    abs(lineweight_mm - std) <= tolerance
                    for std in standard_weights
                )
                
                if not is_standard:
                    self.violations.append(Violation(
                        id=str(uuid.uuid4()),
                        type=ViolationType.LINEWEIGHT,
                        severity=SeverityLevel.WARNING,
                        rule="GB/T 14665-2012 表1 - 线宽规则",
                        description=f"线宽 {lineweight_mm:.2f}mm 不符合标准。标准线宽: {standard_weights}",
                        entity_handle=entity['handle'],
                        layer=entity['layer'],
                        suggestion=f"使用标准线宽: {min(standard_weights, key=lambda x: abs(x-lineweight_mm))}mm"
                    ))
    
    def _check_colors(self, dxf_data: Dict[str, Any]):
        """检查颜色规范"""
        rules = self.rules['colors']
        default_color = rules['default']
        
        # 统计非标准颜色使用
        non_standard_colors = []
        
        for entity_type, entities in dxf_data['entities'].items():
            for entity in entities:
                color = entity.get('color', default_color)
                
                # 检查是否使用了过于花哨的颜色
                if color not in [default_color, 256, 0] and 1 <= color <= 255:
                    non_standard_colors.append((entity, color))
        
        # 如果使用过多颜色，给出提示
        if len(non_standard_colors) > 10:
            self.violations.append(Violation(
                id=str(uuid.uuid4()),
                type=ViolationType.COLOR,
                severity=SeverityLevel.INFO,
                rule="GB/T 14665-2012 表2 - 颜色规则",
                description=f"检测到 {len(non_standard_colors)} 个实体使用了非标准颜色。建议统一使用随层或默认颜色",
                suggestion="将实体颜色设置为 ByLayer（随层）以便统一管理"
            ))
    
    def _check_fonts(self, dxf_data: Dict[str, Any]):
        """检查字体规范"""
        rules = self.rules['fonts']
        min_height = rules['min_height']
        max_height = rules['max_height']
        
        # 检查所有文字高度
        for text in dxf_data['texts']:
            height = text['height']
            
            if height < min_height:
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.FONT,
                    severity=SeverityLevel.WARNING,
                    rule="GB/T 14665-2012 表3 - 字体规则",
                    description=f"文字高度 {height:.1f}mm 过小，最小允许: {min_height}mm",
                    entity_handle=text['handle'],
                    layer=text['layer'],
                    suggestion=f"将文字高度调整至 {min_height}mm 以上"
                ))
            
            elif height > max_height:
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.FONT,
                    severity=SeverityLevel.INFO,
                    rule="GB/T 14665-2012 表3 - 字体规则",
                    description=f"文字高度 {height:.1f}mm 过大，建议不超过: {max_height}mm",
                    entity_handle=text['handle'],
                    layer=text['layer'],
                    suggestion=f"将文字高度调整至 {max_height}mm 以内"
                ))
    
    def _check_dimensions(self, dxf_data: Dict[str, Any]):
        """检查尺寸标注规范"""
        dimensions = dxf_data['dimensions']
        
        if not dimensions:
            return
        
        rules = self.rules['dimensions']
        min_text_height = rules['min_text_height']
        min_arrow_size = rules['min_arrow_size']
        consistency_threshold = rules['consistency_threshold']
        
        # 统计箭头类型（简化实现：通过箭头大小来判断）
        arrow_sizes = [dim['arrow_size'] for dim in dimensions if dim['arrow_size'] > 0]
        
        if arrow_sizes:
            # 检查箭头大小一致性
            arrow_counter = Counter(arrow_sizes)
            most_common_size, count = arrow_counter.most_common(1)[0]
            consistency = count / len(arrow_sizes)
            
            if consistency < consistency_threshold:
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.DIMENSION,
                    severity=SeverityLevel.WARNING,
                    rule="GB/T 14665-2012 6.3节 - 尺寸终端一致性",
                    description=f"尺寸终端类型一致性仅为 {consistency*100:.1f}%，建议达到 {consistency_threshold*100:.0f}%",
                    suggestion=f"统一使用相同的尺寸终端样式（当前主要使用箭头大小: {most_common_size:.1f}mm）"
                ))
        
        # 检查尺寸文字高度
        for dim in dimensions:
            text_height = dim['text_height']
            if text_height > 0 and text_height < min_text_height:
                self.violations.append(Violation(
                    id=str(uuid.uuid4()),
                    type=ViolationType.DIMENSION,
                    severity=SeverityLevel.WARNING,
                    rule="GB/T 14665-2012 - 尺寸文字高度",
                    description=f"尺寸文字高度 {text_height:.1f}mm 过小，最小推荐: {min_text_height}mm",
                    entity_handle=dim['handle'],
                    layer=dim['layer'],
                    suggestion=f"将尺寸文字高度调整至 {min_text_height}mm 以上"
                ))
    
    def _check_geometry_relations(self, dxf_data: Dict[str, Any]):
        """
        Phase 2: 检查几何关系（尺寸线-文字相交、对齐等）
        """
        dimensions = dxf_data.get('dimensions', [])
        texts = dxf_data.get('texts', [])
        
        if not dimensions or not texts:
            return
        
        # 尺寸线与文字相交检测
        violations = self.geometry_engine.check_dimension_text_overlap(dimensions, texts)
        self.violations.extend(violations)
        
        # 尺寸对齐检查
        violations = self.geometry_engine.check_dimension_alignment(dimensions)
        self.violations.extend(violations)
        
        # 尺寸界线间距检查
        violations = self.geometry_engine.check_dimension_extension_line_gap(dimensions)
        self.violations.extend(violations)
    
    def _generate_report(
        self,
        dxf_data: Dict[str, Any],
        analysis_id: str,
        file_id: str
    ) -> ComplianceReport:
        """生成合规性报告"""
        
        # 统计各严重程度的违规数量
        critical_count = sum(1 for v in self.violations if v.severity == SeverityLevel.CRITICAL)
        warning_count = sum(1 for v in self.violations if v.severity == SeverityLevel.WARNING)
        info_count = sum(1 for v in self.violations if v.severity == SeverityLevel.INFO)
        
        # 计算合规得分（简化算法）
        score = 100.0
        score -= critical_count * 10  # 严重错误扣10分
        score -= warning_count * 5    # 警告扣5分
        score -= info_count * 2       # 提示扣2分
        score = max(0, score)  # 最低0分
        
        # 判断是否合规（无严重错误且得分>=80）
        is_compliant = critical_count == 0 and score >= 80
        
        return ComplianceReport(
            analysis_id=analysis_id,
            file_id=file_id,
            filename=dxf_data['filename'],
            standard=self.standard,
            analysis_time=datetime.now(),
            total_violations=len(self.violations),
            critical_count=critical_count,
            warning_count=warning_count,
            info_count=info_count,
            violations=self.violations,
            is_compliant=is_compliant,
            compliance_score=score
        )
