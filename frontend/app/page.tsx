'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import FileUpload from '@/components/FileUpload'
import { uploadFile, startAnalysis } from '@/lib/api'

export default function Home() {
  const router = useRouter()
  const [uploading, setUploading] = useState(false)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [testingDemo, setTestingDemo] = useState(false)

  const handleFileUpload = async (file: File) => {
    setError(null)
    setUploading(true)
    setAnalyzing(true)

    try {
      // 上传并分析（合并为一个 API 调用）
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch('/api/check', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '处理失败')
      }
      
      const data = await response.json()
      console.log('分析完成:', data)

      // 保存报告到 localStorage
      if (data.report) {
        localStorage.setItem(
          `report_${data.analysis_id}`,
          JSON.stringify(data.report)
        )
      }

      // 跳转到结果页面
      router.push(`/result/${data.analysis_id}`)
    } catch (err: any) {
      setError(err.message || '操作失败，请重试')
    } finally {
      setUploading(false)
      setAnalyzing(false)
    }
  }

  const handleDemoTest = async () => {
    setError(null)
    setTestingDemo(true)
    setAnalyzing(true)

    try {
      // 本地生成演示报告，无需调用后端
      const demoId = `demo_${Date.now()}`
      const demoReport = {
        analysis_id: demoId,
        file_id: 'demo_file_001',
        filename: '示例图纸.dxf',
        standard: 'GB/T 14665-2012',
        analysis_time: new Date().toISOString(),
        total_violations: 6,
        critical_count: 2,
        warning_count: 3,
        info_count: 1,
        is_compliant: false,
        compliance_score: 76.5,
        violations: [
          {
            id: 'v1',
            type: '图层错误',
            severity: '严重',
            rule: '图层命名必须符合企业命名规范',
            description: '发现未按规范命名的图层：Layer1、NewLayer。',
            layer: 'Layer1',
            suggestion: '统一使用规范命名，例如：DIM_、TEXT_、CENTER_ 前缀分类。'
          },
          {
            id: 'v2',
            type: '线宽错误',
            severity: '严重',
            rule: '主要轮廓线宽应为 0.5mm 或 0.35mm',
            description: '检测到 0.13mm 的主轮廓线，过细不符合阅读要求。',
            layer: 'OUTLINE',
            suggestion: '将主轮廓线的线宽设置为 0.5mm 或 0.35mm。'
          },
          {
            id: 'v3',
            type: '字体错误',
            severity: '警告',
            rule: '文字应使用统一字体（如 GB/T 14665 推荐字体）',
            description: '部分文字使用了 Arial 字体。',
            layer: 'TEXT',
            suggestion: '将字体统一为 gbenor 或仿宋等规范字体。'
          },
          {
            id: 'v4',
            type: '尺寸标注错误',
            severity: '警告',
            rule: '尺寸线与箭头样式应一致且尺寸单位明确',
            description: '检测到两种不同箭头样式，且部分标注未显示单位。',
            layer: 'DIM',
            suggestion: '统一标注样式，确保单位显示为 mm。'
          },
          {
            id: 'v5',
            type: '颜色错误',
            severity: '提示',
            rule: '按图层出图，颜色使用 ByLayer',
            description: '若干实体设置了 ByObject 颜色，可能导致出图不一致。',
            suggestion: '将实体颜色改为 ByLayer。'
          },
          {
            id: 'v6',
            type: '几何错误',
            severity: '警告',
            rule: '同心圆与圆心应完全重合',
            description: '检测到同心圆偏心 0.2mm。',
            suggestion: '调整圆心坐标，确保重合。'
          }
        ]
      }

      localStorage.setItem(`report_${demoId}`, JSON.stringify(demoReport))
      router.push(`/result/${demoId}`)
    } catch (err: any) {
      setError(err.message || '演示加载失败，请重试')
    } finally {
      setTestingDemo(false)
      setAnalyzing(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* 头部 */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            CAD 规范符合性检查
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            AI 驱动的自动化 CAD 图纸检查系统 · 支持 GB/T 14665-2012 标准
          </p>
        </div>

        {/* 上传区域 */}
        <div className="max-w-3xl mx-auto">
          <FileUpload
            onFileSelect={handleFileUpload}
            uploading={uploading}
            analyzing={analyzing}
          />

          {/* 演示按钮 */}
          <div className="mt-6 text-center">
            <button
              onClick={handleDemoTest}
              disabled={testingDemo || uploading || analyzing}
              className="
                px-8 py-3 rounded-lg font-medium text-white
                bg-gradient-to-r from-purple-500 to-indigo-600
                hover:from-purple-600 hover:to-indigo-700
                disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed
                transition-all duration-300 shadow-md hover:shadow-lg
                transform hover:scale-105 disabled:transform-none
              "
            >
              {testingDemo ? '加载演示中...' : '🎯 查看演示报告'}
            </button>
            <p className="text-sm text-gray-500 mt-2">
              没有 CAD 文件？点击查看示例检查报告
            </p>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* 状态提示 */}
          {(uploading || analyzing) && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800 text-center">
                {uploading && '正在上传文件...'}
                {testingDemo && '正在加载演示报告...'}
                {analyzing && !testingDemo && '正在分析图纸，请稍候...'}
              </p>
            </div>
          )}
        </div>

        {/* 功能特点 */}
        <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2">快速分析</h3>
            <p className="text-gray-600">
              30秒内完成标准DXF文件的全面检查
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">精准识别</h3>
            <p className="text-gray-600">
              自动检测图层、线宽、字体、尺寸等规范问题
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-md">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">详细报告</h3>
            <p className="text-gray-600">
              提供完整的违规分析和修复建议
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
