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
      // 使用示例 DXF 文件进行测试
      const response = await fetch('/api/demo', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ useDemo: true })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || '演示加载失败')
      }
      
      const data = await response.json()
      console.log('演示分析完成:', data)

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
