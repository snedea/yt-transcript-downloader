# Testing Guide

This document describes how to run and write tests for the YouTube Transcript Downloader.

## Overview

The project uses:
- **Backend:** pytest with pytest-asyncio
- **Frontend:** Jest with React Testing Library

## Backend Testing

### Prerequisites

Install development dependencies:

```bash
cd backend
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Running Tests

**Run all tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ -v --cov=app --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/test_youtube.py -v
```

**Run specific test:**
```bash
pytest tests/test_youtube.py::test_get_transcript -v
```

**Skip integration tests (no OpenAI required):**
```bash
pytest tests/ -v -m "not integration"
```

### Test Structure

```
backend/tests/
├── conftest.py           # Shared fixtures
├── test_youtube.py       # YouTube service tests
├── test_openai.py        # OpenAI service tests
├── test_playlist.py      # Playlist service tests
└── test_url_parser.py    # URL parser tests
```

### Writing Backend Tests

**Example: Testing a Service**

```python
# tests/test_youtube.py
import pytest
from app.services.youtube import YouTubeService

@pytest.fixture
def youtube_service():
    return YouTubeService()

def test_get_transcript(youtube_service):
    # Use a video known to have transcripts
    video_id = "dQw4w9WgXcQ"
    transcript = youtube_service.get_transcript(video_id)

    assert transcript is not None
    assert len(transcript) > 0
    assert isinstance(transcript, str)

def test_invalid_video_id(youtube_service):
    with pytest.raises(Exception):
        youtube_service.get_transcript("invalid_id_12345")
```

**Example: Testing an Endpoint**

```python
# tests/test_endpoints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_single_transcript_endpoint(client):
    response = client.post(
        "/api/transcript/single",
        json={"video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    assert response.status_code == 200
    assert "transcript" in response.json()
```

**Example: Async Test**

```python
# tests/test_async.py
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    from app.services.youtube import YouTubeService
    service = YouTubeService()
    result = await service.async_get_transcript("dQw4w9WgXcQ")
    assert result is not None
```

### Test Markers

```python
@pytest.mark.integration  # Requires external services
@pytest.mark.slow         # Takes longer than 5 seconds
@pytest.mark.skip         # Skip this test
```

### Mocking External Services

```python
from unittest.mock import Mock, patch

def test_with_mock():
    with patch('app.services.youtube.YouTubeTranscriptApi') as mock_api:
        mock_api.return_value.get_transcript.return_value = [
            {"text": "Hello", "start": 0, "duration": 1}
        ]

        service = YouTubeService()
        result = service.get_transcript("test_id")

        assert result == "Hello"
        mock_api.return_value.get_transcript.assert_called_once()
```

## Frontend Testing

### Prerequisites

```bash
cd frontend
npm install
```

### Running Tests

**Run all tests:**
```bash
npm test
```

**Run in watch mode:**
```bash
npm test -- --watch
```

**Run with coverage:**
```bash
npm test -- --coverage
```

**Run specific test file:**
```bash
npm test -- SingleDownload.test.tsx
```

### Test Structure

```
frontend/src/
├── __tests__/
│   ├── components/
│   │   ├── SingleDownload.test.tsx
│   │   ├── BulkDownload.test.tsx
│   │   └── TranscriptDisplay.test.tsx
│   ├── hooks/
│   │   ├── useTranscript.test.ts
│   │   └── useBulkDownload.test.ts
│   └── services/
│       └── api.test.ts
```

### Writing Frontend Tests

**Example: Component Test**

```typescript
// __tests__/components/SingleDownload.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SingleDownload from '@/components/SingleDownload';

describe('SingleDownload', () => {
  it('renders input field', () => {
    render(<SingleDownload />);

    expect(screen.getByPlaceholderText(/youtube url/i)).toBeInTheDocument();
  });

  it('shows loading state when fetching', async () => {
    render(<SingleDownload />);

    const input = screen.getByPlaceholderText(/youtube url/i);
    const button = screen.getByRole('button', { name: /get transcript/i });

    fireEvent.change(input, { target: { value: 'https://youtube.com/watch?v=abc123' } });
    fireEvent.click(button);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays error for invalid URL', async () => {
    render(<SingleDownload />);

    const input = screen.getByPlaceholderText(/youtube url/i);
    const button = screen.getByRole('button', { name: /get transcript/i });

    fireEvent.change(input, { target: { value: 'invalid-url' } });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/invalid/i)).toBeInTheDocument();
    });
  });
});
```

**Example: Hook Test**

```typescript
// __tests__/hooks/useTranscript.test.ts
import { renderHook, act } from '@testing-library/react';
import { useTranscript } from '@/hooks/useTranscript';

describe('useTranscript', () => {
  it('initializes with empty state', () => {
    const { result } = renderHook(() => useTranscript());

    expect(result.current.transcript).toBe('');
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(null);
  });

  it('sets loading state when fetching', async () => {
    const { result } = renderHook(() => useTranscript());

    act(() => {
      result.current.fetchTranscript('https://youtube.com/watch?v=abc123');
    });

    expect(result.current.loading).toBe(true);
  });
});
```

**Example: Mocking API Calls**

```typescript
// __tests__/services/api.test.ts
import axios from 'axios';
import { api } from '@/services/api';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Service', () => {
  it('fetches transcript successfully', async () => {
    mockedAxios.post.mockResolvedValueOnce({
      data: {
        transcript: 'Test transcript',
        video_title: 'Test Video',
        video_id: 'abc123'
      }
    });

    const result = await api.getTranscript('https://youtube.com/watch?v=abc123');

    expect(result.transcript).toBe('Test transcript');
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/api/transcript/single'),
      expect.any(Object)
    );
  });
});
```

### Testing Best Practices

1. **Test behavior, not implementation**
2. **Use meaningful test descriptions**
3. **Keep tests independent**
4. **Mock external dependencies**
5. **Test error states**
6. **Test accessibility**

## End-to-End Testing

For E2E testing, you can use Playwright (already in devDependencies):

```bash
# Install browsers
npx playwright install

# Run E2E tests
npx playwright test
```

**Example E2E Test:**

```typescript
// e2e/transcript.spec.ts
import { test, expect } from '@playwright/test';

test('download single transcript', async ({ page }) => {
  await page.goto('http://localhost:3000');

  await page.fill('input[placeholder*="YouTube"]', 'https://youtube.com/watch?v=dQw4w9WgXcQ');
  await page.click('button:has-text("Get Transcript")');

  await expect(page.locator('.transcript-content')).toBeVisible({ timeout: 30000 });
  await expect(page.locator('.transcript-content')).toContainText(/./);
});
```

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd backend
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
          pytest tests/ -v --cov=app

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd frontend
          npm install
          npm test -- --coverage
```

## Test Coverage Goals

| Component | Target Coverage |
|-----------|----------------|
| Backend Services | 80% |
| Backend Routers | 70% |
| Frontend Components | 70% |
| Frontend Hooks | 80% |
| Utilities | 90% |

View coverage reports:
- **Backend:** `htmlcov/index.html` after running with `--cov-report=html`
- **Frontend:** `coverage/lcov-report/index.html` after running with `--coverage`
