import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://cad-backend:8000'

export async function POST(request: NextRequest) {
  try {
    // 获取上传的文件
    const formData = await request.formData()
    
    // 转发到后端
    const response = await fetch(`${BACKEND_URL}/api/v1/upload`, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error: any) {
    console.error('Upload proxy error:', error)
    return NextResponse.json(
      { detail: error.message || 'Upload failed' },
      { status: 500 }
    )
  }
}
