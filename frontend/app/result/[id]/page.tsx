'use client'

import { useParams } from 'next/navigation'
import { useEffect, useState } from 'react'
import type { ComplianceReport } from '@/types'

export default function ResultPage() {
  const params = useParams()
  const id = params.id as string
  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // 从 localStorage 获取报告数据
    const reportData = localStorage.getItem(`report_${id}`)
    if (reportData) {
      try {
        setReport(JSON.parse(reportData))
      } catch (e) {
        setError('无法解析报告数据')
      }
    } else {
      setError('未找到报告数据')
    }
    setLoading(false)
  }, [id])

  const copyToClipboard = () => {
    if (report) {
      navigator.clipboard.writeText(JSON.stringify(report, null, 2))
      alert('报告已复制到剪贴板')
    }
  }

  const downloadJSON = () => {
    if (report) {
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `CAD检查报告_${report.filename}_${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case '严重':
        return 'text-red-600 bg-red-50'
      case '警告':
        return 'text-orange-600 bg-orange-50'
      case '提示':
        return 'text-blue-600 bg-blue-50'
      default:
        return 'text-gray-600 bg-gray-50'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载报告中...</p>
        </div>
      </div>
    )
  }

  if (error || !report) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-lg">{error || '报告不存在'}</p>
          <a href="/" className="mt-4 inline-block text-blue-600 hover:underline">
            返回首页
          </a>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* 报告头部 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-800">合规性检查报告</h1>
            <div className="flex gap-3">
              <button
                onClick={copyToClipboard}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
              >
                📋 复制报告
              </button>
              <button
                onClick={downloadJSON}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                ⬇️ 下载 JSON
              </button>
            </div>
          </div>

          {/* 文件信息 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-500">文件名：</span>
              <span className="font-medium">{report.filename}</span>
            </div>
            <div>
              <span className="text-gray-500">检查标准：</span>
              <span className="font-medium">{report.standard}</span>
            </div>
            <div>
              <span className="text-gray-500">分析时间：</span>
              <span className="font-medium">
                {new Date(report.analysis_time).toLocaleString('zh-CN')}
              </span>
            </div>
            <div>
              <span className="text-gray-500">合规得分：</span>
              <span className={`font-bold ${report.compliance_score >= 80 ? 'text-green-600' : 'text-red-600'}`}>
                {report.compliance_score.toFixed(1)} / 100
              </span>
            </div>
          </div>
        </div>

        {/* 统计摘要 */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-500 mb-1">总违规数</div>
            <div className="text-3xl font-bold text-gray-800">{report.total_violations}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-500 mb-1">严重错误</div>
            <div className="text-3xl font-bold text-red-600">{report.critical_count}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-500 mb-1">警告</div>
            <div className="text-3xl font-bold text-orange-600">{report.warning_count}</div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="text-sm text-gray-500 mb-1">提示</div>
            <div className="text-3xl font-bold text-blue-600">{report.info_count}</div>
          </div>
        </div>

        {/* 合规状态 */}
        <div className={`rounded-lg p-6 mb-6 ${report.is_compliant ? 'bg-green-50 border-2 border-green-200' : 'bg-red-50 border-2 border-red-200'}`}>
          <div className="flex items-center">
            <span className="text-4xl mr-4">{report.is_compliant ? '✅' : '❌'}</span>
            <div>
              <h2 className={`text-2xl font-bold ${report.is_compliant ? 'text-green-700' : 'text-red-700'}`}>
                {report.is_compliant ? '图纸合规' : '图纸不合规'}
              </h2>
              <p className="text-gray-600 mt-1">
                {report.is_compliant
                  ? '恭喜！您的图纸符合 GB/T 14665-2012 标准要求。'
                  : '检测到不符合规范的项目，请根据下列建议进行修改。'}
              </p>
            </div>
          </div>
        </div>

        {/* 违规详情 */}
        {report.violations.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">违规详情</h2>
            <div className="space-y-4">
              {report.violations.map((violation, index) => (
                <div key={violation.id} className="border rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className="text-lg font-semibold text-gray-500">#{index + 1}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(violation.severity)}`}>
                        {violation.severity}
                      </span>
                      <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-medium text-gray-700">
                        {violation.type}
                      </span>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <span className="text-sm text-gray-500">规则：</span>
                    <span className="text-sm font-medium text-gray-700 ml-2">{violation.rule}</span>
                  </div>
                  
                  <p className="text-gray-800 mb-2">{violation.description}</p>
                  
                  {violation.suggestion && (
                    <div className="bg-blue-50 border-l-4 border-blue-400 p-3 mt-2">
                      <p className="text-sm text-blue-800">
                        <span className="font-semibold">💡 建议：</span> {violation.suggestion}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex gap-4 mt-3 text-xs text-gray-500">
                    {violation.entity_handle && (
                      <span>句柄: {violation.entity_handle}</span>
                    )}
                    {violation.layer && (
                      <span>图层: {violation.layer}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {report.violations.length === 0 && (
          <div className="bg-green-50 border-2 border-green-200 rounded-lg p-8 text-center">
            <span className="text-6xl mb-4 block">🎉</span>
            <h2 className="text-2xl font-bold text-green-700 mb-2">完美！</h2>
            <p className="text-gray-600">未发现任何违规项目，图纸完全符合规范。</p>
          </div>
        )}

        {/* 返回按钮 */}
        <div className="mt-8 text-center">
          <a
            href="/"
            className="inline-block px-8 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition"
          >
            ← 返回首页
          </a>
        </div>
      </div>
    </div>
  )
}
