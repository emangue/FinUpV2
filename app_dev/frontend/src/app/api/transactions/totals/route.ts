import { NextResponse } from 'next/server';

const BACKEND_URL = 'http://localhost:8000';

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/v1/transactions/totals`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching transaction totals:', error);
    return NextResponse.json(
      { error: 'Failed to fetch transaction totals' },
      { status: 500 }
    );
  }
}