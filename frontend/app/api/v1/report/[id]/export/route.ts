import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://103.109.20.169:10437'

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params
    const { searchParams } = new URL(request.url)
    const format = searchParams.get('format') || 'json'
    
    const response = await fetch(`${BACKEND_URL}/api/v1/report/${id}/export?format=${format}`)

    if (!response.ok) {
      const error = await response.json()
      return NextResponse.json(error, { status: response.status })
    }

    // 转发二进制响应
    const blob = await response.blob()
    return new NextResponse(blob, {
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/octet-stream',
        'Content-Disposition': response.headers.get('Content-Disposition') || `attachment; filename=report_${id}.${format}`
      }
    })
  } catch (error: any) {
    console.error('Report export proxy error:', error)
    return NextResponse.json(
      { detail: error.message || 'Failed to export report' },
      { status: 500 }
    )
  }
}
