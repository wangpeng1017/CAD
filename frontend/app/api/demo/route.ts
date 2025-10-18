import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'
import FormData from 'form-data'

const BACKEND_URL = process.env.BACKEND_URL || 'http://103.109.20.169:10437'

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type') || ''

    if (!contentType.includes('application/json')) {
      return NextResponse.json({ error: '仅支持 application/json 请求' }, { status: 400 })
    }

    const body = await request.json()
    if (!body?.useDemo) {
      return NextResponse.json({ error: '缺少 useDemo 标识' }, { status: 400 })
    }

    // 读取示例 DXF 文件（项目根目录 test_sample.dxf）
    const demoFilePath = join(process.cwd(), '..', 'test_sample.dxf')
    const fileBuffer = await readFile(demoFilePath)

    // 通过后端上传+分析+获取报告
    const formData = new FormData()
    formData.append('file', fileBuffer, {
      filename: 'demo_sample.dxf',
      contentType: 'application/dxf',
    })

    const uploadResponse = await fetch(`${BACKEND_URL}/api/v1/upload`, {
      method: 'POST',
      body: formData as any,
      headers: formData.getHeaders(),
    })

    if (!uploadResponse.ok) {
      const error = await safeJson(uploadResponse)
      return NextResponse.json(
        { error: `演示文件上传失败: ${error?.detail || error?.error || uploadResponse.statusText}` },
        { status: uploadResponse.status }
      )
    }
    const uploadData = await uploadResponse.json()

    const analyzeResponse = await fetch(`${BACKEND_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id: uploadData.file_id, standard: 'GB/T 14665-2012' }),
    })
    if (!analyzeResponse.ok) {
      const error = await safeJson(analyzeResponse)
      return NextResponse.json(
        { error: `分析失败: ${error?.detail || error?.error || analyzeResponse.statusText}` },
        { status: analyzeResponse.status }
      )
    }
    const analyzeData = await analyzeResponse.json()

    const reportResponse = await fetch(`${BACKEND_URL}/api/v1/report/${analyzeData.analysis_id}`)
    if (!reportResponse.ok) {
      const error = await safeJson(reportResponse)
      return NextResponse.json(
        { error: `获取报告失败: ${error?.detail || error?.error || reportResponse.statusText}` },
        { status: reportResponse.status }
      )
    }
    const reportData = await reportResponse.json()

    return NextResponse.json({
      analysis_id: analyzeData.analysis_id,
      file_id: uploadData.file_id,
      report: reportData,
      message: '演示报告加载成功',
    })
  } catch (err: any) {
    console.error('Demo API error:', err)
    return NextResponse.json({ error: err.message || '处理失败' }, { status: 500 })
  }
}

async function safeJson(res: Response) {
  try {
    return await res.json()
  } catch {
    return null
  }
}
