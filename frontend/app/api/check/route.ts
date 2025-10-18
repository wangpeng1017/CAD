import { NextRequest, NextResponse } from 'next/server'
import { readFile } from 'fs/promises'
import { join } from 'path'

const BACKEND_URL = process.env.BACKEND_URL || 'http://103.109.20.169:10437'

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type')
    
    // 处理演示请求
    if (contentType?.includes('application/json')) {
      const body = await request.json()
      
      if (body.useDemo) {
        // 读取示例 DXF 文件
        const demoFilePath = join(process.cwd(), '..', 'test_sample.dxf')
        
        try {
          const fileBuffer = await readFile(demoFilePath)
          const blob = new Blob([fileBuffer], { type: 'application/dxf' })
          const formData = new FormData()
          formData.append('file', blob, 'demo_sample.dxf')
          
          // 上传到后端
          const uploadResponse = await fetch(`${BACKEND_URL}/api/v1/upload`, {
            method: 'POST',
            body: formData,
          })
          
          if (!uploadResponse.ok) {
            const error = await uploadResponse.json()
            return NextResponse.json(
              { error: '演示文件上传失败: ' + (error.detail || '未知错误') },
              { status: uploadResponse.status }
            )
          }
          
          const uploadData = await uploadResponse.json()
          
          // 开始分析
          const analyzeResponse = await fetch(`${BACKEND_URL}/api/v1/analyze`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              file_id: uploadData.file_id,
              standard: 'GB/T 14665-2012'
            }),
          })
          
          if (!analyzeResponse.ok) {
            const error = await analyzeResponse.json()
            return NextResponse.json(
              { error: '分析失败: ' + (error.detail || '未知错误') },
              { status: analyzeResponse.status }
            )
          }
          
          const analyzeData = await analyzeResponse.json()
          
          // 获取报告
          const reportResponse = await fetch(
            `${BACKEND_URL}/api/v1/report/${analyzeData.analysis_id}`
          )
          
          if (!reportResponse.ok) {
            const error = await reportResponse.json()
            return NextResponse.json(
              { error: '获取报告失败: ' + (error.detail || '未知错误') },
              { status: reportResponse.status }
            )
          }
          
          const reportData = await reportResponse.json()
          
          return NextResponse.json({
            analysis_id: analyzeData.analysis_id,
            file_id: uploadData.file_id,
            report: reportData,
            message: '演示报告加载成功'
          })
          
        } catch (fileError: any) {
          console.error('Demo file error:', fileError)
          return NextResponse.json(
            { error: '找不到演示文件，请联系管理员' },
            { status: 404 }
          )
        }
      }
    }
    
    // 处理实际文件上传
    const formData = await request.formData()
    const file = formData.get('file')
    
    if (!file) {
      return NextResponse.json(
        { error: '未提供文件' },
        { status: 400 }
      )
    }
    
    // 上传到后端
    const uploadResponse = await fetch(`${BACKEND_URL}/api/v1/upload`, {
      method: 'POST',
      body: formData,
    })
    
    if (!uploadResponse.ok) {
      const error = await uploadResponse.json()
      return NextResponse.json(
        { error: '文件上传失败: ' + (error.detail || '未知错误') },
        { status: uploadResponse.status }
      )
    }
    
    const uploadData = await uploadResponse.json()
    
    // 开始分析
    const analyzeResponse = await fetch(`${BACKEND_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_id: uploadData.file_id,
        standard: 'GB/T 14665-2012'
      }),
    })
    
    if (!analyzeResponse.ok) {
      const error = await analyzeResponse.json()
      return NextResponse.json(
        { error: '分析失败: ' + (error.detail || '未知错误') },
        { status: analyzeResponse.status }
      )
    }
    
    const analyzeData = await analyzeResponse.json()
    
    // 获取报告
    const reportResponse = await fetch(
      `${BACKEND_URL}/api/v1/report/${analyzeData.analysis_id}`
    )
    
    if (!reportResponse.ok) {
      const error = await reportResponse.json()
      return NextResponse.json(
        { error: '获取报告失败: ' + (error.detail || '未知错误') },
        { status: reportResponse.status }
      )
    }
    
    const reportData = await reportResponse.json()
    
    return NextResponse.json({
      analysis_id: analyzeData.analysis_id,
      file_id: uploadData.file_id,
      report: reportData,
      message: '分析完成'
    })
    
  } catch (error: any) {
    console.error('Check API error:', error)
    return NextResponse.json(
      { error: error.message || '处理失败' },
      { status: 500 }
    )
  }
}
