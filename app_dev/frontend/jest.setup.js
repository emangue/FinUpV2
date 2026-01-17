import '@testing-library/jest-dom'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      back: jest.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
}))

// Mock window.alert
global.alert = jest.fn()

// Mock fetch
global.fetch = jest.fn()

// Setup fetch mock
beforeEach(() => {
  fetch.mockClear()
})