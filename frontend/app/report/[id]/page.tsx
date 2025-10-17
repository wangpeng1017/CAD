'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { getReport, getAnalysisStatus, exportReport } from '@/lib/api'
import { ComplianceReport, AnalysisStatus } from '@/types'

export default function ReportPage() {
  const params = useParams()
  const router = useRouter()
  const analysisId = params.id as string

  const [status, setStatus] = useState<AnalysisStatus>('pending')
  const [report, setReport] = useState<ComplianceReport | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (!analysisId) return

    const checkStatus = async () => {
      try {
        const statusResponse = await getAnalysisStatus(analysisId)
        setStatus(statusResponse.status)

        if (statusResponse.status === 'completed') {
          // 分析完成，获取报告
          const reportData = await getReport(analysisId)
          setReport(reportData)
          setPolling(false)
        } else if (statusResponse.status === 'failed') {
          // 获取详细错误信息
          setError(statusResponse.message || '分析失败，请重试')
          setPolling(false)
        }
      } catch (err: any) {
        console.error('Error checking status:', err)
        // 继续轮询，不立即显示错误
      }
    }

    // 立即检查一次
    checkStatus()

    // 如果还在处理中，每2秒轮询一次
    const interval = polling ? setInterval(checkStatus, 2000) : null

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [analysisId, polling])

  const handleExport = async (format: 'json' | 'html') => {
    try {
      await exportReport(analysisId, format)
    } catch (err) {
      alert('导出失败，请重试')
    }
  }

  if (error) {
    const isDwgError = error.includes('DWG') || error.includes('转换')
    
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="max-w-2xl w-full">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">❌</div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">分析失败</h1>
            </div>
            
            {/* 错误信息 */}
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-red-800 whitespace-pre-wrap">{error}</p>
            </div>
            
            {/* DWG 格式提示 */}
            {isDwgError && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2">💡 解决方案：</h3>
                <ol className="list-decimal list-inside space-y-2 text-sm text-blue-800">
                  <li>在 AutoCAD 或其他 CAD 软件中打开原始 DWG 文件</li>
                  <li>使用 <strong>“文件 → 另存为”</strong> 功能</li>
                  <li>选择文件类型为 <strong>“AutoCAD DXF (*.dxf)”</strong></li>
                  <li>保存后重新上传 DXF 文件</li>
                </ol>
                <p className="mt-3 text-xs text-blue-700">
                  ⚠️ 提示：DXF 是开放格式，比 DWG 更适合用于合规性检查。
                </p>
              </div>
            )}
            
            {/* 操作按钮 */}
            <div className="flex gap-4">
              <button
                onClick={() => router.push('/')}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                返回首页
              </button>
              <button
                onClick={() => window.open('/docs/DWG_FORMAT_GUIDE.md', '_blank')}
                className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                查看帮助文档
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            {status === 'pending' && '分析排队中...'}
            {status === 'processing' && '正在分析图纸...'}
          </h2>
          <p className="text-gray-600">请稍候，通常需要 10-30 秒</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/')}
            className="mb-4 text-blue-600 hover:text-blue-800 flex items-center"
          >
            ← 返回首页
          </button>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            检查报告
          </h1>
          <p className="text-gray-600">
            文件：{report.filename} · 标准：{report.standard}
          </p>
        </div>

        {/* 总结卡片 */}
        <div className={`rounded-xl p-8 mb-8 ${
          report.is_compliant 
            ? 'bg-green-50 border-2 border-green-200' 
            : 'bg-red-50 border-2 border-red-200'
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold mb-2">
                {report.is_compliant ? '✓ 合规' : '✗ 不合规'}
              </h2>
              <p className="text-lg">
                合规得分：<span className="font-bold">{report.compliance_score.toFixed(1)}</span> / 100
              </p>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold mb-1">{report.total_violations}</div>
              <div className="text-sm text-gray-600">违规项</div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4 mt-6">
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-red-600">{report.critical_count}</div>
              <div className="text-sm text-gray-600">严重错误</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-yellow-600">{report.warning_count}</div>
              <div className="text-sm text-gray-600">警告</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-2xl font-bold text-blue-600">{report.info_count}</div>
              <div className="text-sm text-gray-600">提示</div>
            </div>
          </div>
        </div>

        {/* 导出按钮 */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={() => handleExport('json')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            📥 导出 JSON
          </button>
          <button
            onClick={() => handleExport('html')}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
          >
            📄 导出 HTML
          </button>
        </div>

        {/* 违规列表 */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-2xl font-bold mb-6">违规详情</h2>

          {report.violations.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <div className="text-5xl mb-4">🎉</div>
              <p className="text-lg">未发现任何违规项！</p>
            </div>
          ) : (
            <div className="space-y-4">
              {report.violations.map((violation) => (
                <div
                  key={violation.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        violation.severity === '严重' 
                          ? 'bg-red-100 text-red-800'
                          : violation.severity === '警告'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {violation.severity}
                      </span>
                      <span className="text-sm font-medium text-gray-700">
                        {violation.type}
                      </span>
                    </div>
                    {violation.layer && (
                      <span className="text-xs text-gray-500">
                        图层: {violation.layer}
                      </span>
                    )}
                  </div>

                  <div className="mb-2">
                    <p className="text-sm text-gray-600 mb-1">
                      <strong>规则:</strong> {violation.rule}
                    </p>
                    <p className="text-gray-800">{violation.description}</p>
                  </div>

                  {violation.suggestion && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-md">
                      <p className="text-sm text-blue-900">
                        <strong>💡 建议:</strong> {violation.suggestion}
                      </p>
                    </div>
                  )}

                  {violation.entity_details && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-md">
                      <p className="text-sm font-semibold text-gray-700 mb-2">实体信息</p>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                        {Object.entries(violation.entity_details).map(([key, value]) => (
                          <div key={key} className="flex">
                            <div className="w-28 text-gray-500">{key}</div>
                            <div className="flex-1 break-all">{typeof value === 'object' ? JSON.stringify(value) : String(value)}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {violation.entity_handle && (
                    <div className="mt-2 text-xs text-gray-500">
                      实体句柄: {violation.entity_handle}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
