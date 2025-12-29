"""
Comprehensive tests for the new litellm-based AIClient with OpenRouter integration.
Tests both real API calls (when OPEN_ROUTER_API_KEY is set) and mock behavior.
"""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.ai.ai_client import AIClient, MockAIClient
from app.models import Decision, Vote
from app.config import config


# Fixtures for test data
@pytest.fixture
def mock_decision():
    """Create a mock decision for testing."""
    decision = Decision(
        id=1,
        text="Should we deploy the new feature?",
        status="pending",
        proposer_phone="user123",
        proposer_name="User One",
        channel_id="channel456",
        team_id="team789",
        zoho_org_id="org001",
        group_size_at_creation=5,
        approval_threshold=3,
        approval_count=2,
        rejection_count=1,
    )
    return decision


@pytest.fixture
def mock_votes():
    """Create mock votes for testing."""
    return [
        Vote(id=1, decision_id=1, voter_phone="user1", voter_name="Alice", vote_type="approve"),
        Vote(id=2, decision_id=1, voter_phone="user2", voter_name="Bob", vote_type="approve"),
        Vote(id=3, decision_id=1, voter_phone="user3", voter_name="Charlie", vote_type="reject"),
    ]


@pytest.fixture
def empty_votes():
    """Create an empty vote list for testing."""
    return []


# Test MockAIClient (always works)
class TestMockAIClient:
    """Tests for MockAIClient - should always work."""
    
    def test_mock_client_initialization(self):
        """Test MockAIClient initializes without errors."""
        client = MockAIClient()
        assert client is not None
    
    def test_mock_summarize_decision(self, mock_decision, mock_votes):
        """Test MockAIClient.summarize_decision returns test mode message."""
        client = MockAIClient()
        result = client.summarize_decision(mock_decision, mock_votes)
        assert result == "🤖 AI Summary (test mode)"
        assert isinstance(result, str)
    
    def test_mock_suggest_next_steps(self, mock_decision, mock_votes):
        """Test MockAIClient.suggest_next_steps returns test mode message."""
        client = MockAIClient()
        result = client.suggest_next_steps(mock_decision, mock_votes)
        assert result == "🤖 AI Suggestions (test mode)"
        assert isinstance(result, str)
    
    def test_mock_with_empty_votes(self, mock_decision, empty_votes):
        """Test MockAIClient works with empty votes."""
        client = MockAIClient()
        
        summary = client.summarize_decision(mock_decision, empty_votes)
        suggestions = client.suggest_next_steps(mock_decision, empty_votes)
        
        assert summary == "🤖 AI Summary (test mode)"
        assert suggestions == "🤖 AI Suggestions (test mode)"


# Test AIClient with mocked litellm
class TestAIClientWithMockedLiteLLM:
    """Tests for AIClient with litellm mocked."""
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_client_initialization_success(self, mock_litellm):
        """Test AIClient initializes successfully with valid API key."""
        client = AIClient()
        assert client.initialized is True
        assert client.api_key == 'test-api-key'
        assert client.model == 'openrouter/google/gemini-2.5-flash-lite'
    
    @patch('app.ai.ai_client.litellm', None)
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_client_initialization_no_litellm(self):
        """Test AIClient handles missing litellm gracefully."""
        client = AIClient()
        assert client.initialized is False
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', '')
    def test_client_initialization_no_api_key(self, mock_litellm):
        """Test AIClient handles missing API key gracefully."""
        client = AIClient()
        assert client.initialized is False
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_summarize_decision_success(self, mock_litellm, mock_decision, mock_votes):
        """Test summarize_decision with successful API response."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This decision involves deploying a new feature with 2 approvals and 1 rejection."
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.summarize_decision(mock_decision, mock_votes)
        
        assert result == "This decision involves deploying a new feature with 2 approvals and 1 rejection."
        mock_litellm.completion.assert_called_once()
        call_args = mock_litellm.completion.call_args
        assert call_args.kwargs['model'] == 'openrouter/google/gemini-2.5-flash-lite'
        assert 'messages' in call_args.kwargs
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_summarize_decision_empty_votes(self, mock_litellm, mock_decision, empty_votes):
        """Test summarize_decision with empty votes list."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "No votes yet summary."
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.summarize_decision(mock_decision, empty_votes)
        
        assert result == "No votes yet summary."
        # Verify the prompt mentions "No votes yet"
        call_args = mock_litellm.completion.call_args
        prompt = call_args.kwargs['messages'][0]['content']
        assert "No votes yet" in prompt
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_suggest_next_steps_success(self, mock_litellm, mock_decision, mock_votes):
        """Test suggest_next_steps with successful API response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1. Continue gathering votes. 2. Consider discussion round. 3. Set deadline."
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.suggest_next_steps(mock_decision, mock_votes)
        
        assert result == "1. Continue gathering votes. 2. Consider discussion round. 3. Set deadline."
        mock_litellm.completion.assert_called_once()
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_suggest_next_steps_empty_votes(self, mock_litellm, mock_decision, empty_votes):
        """Test suggest_next_steps with empty votes list."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Next steps suggestions."
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.suggest_next_steps(mock_decision, empty_votes)
        
        assert result == "Next steps suggestions."
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_summarize_decision_api_error(self, mock_litellm, mock_decision, mock_votes):
        """Test summarize_decision handles API errors gracefully."""
        mock_litellm.completion.side_effect = Exception("API Error")
        
        client = AIClient()
        result = client.summarize_decision(mock_decision, mock_votes)
        
        assert result is None
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_suggest_next_steps_api_error(self, mock_litellm, mock_decision, mock_votes):
        """Test suggest_next_steps handles API errors gracefully."""
        mock_litellm.completion.side_effect = Exception("API Error")
        
        client = AIClient()
        result = client.suggest_next_steps(mock_decision, mock_votes)
        
        assert result is None
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_summarize_decision_empty_response(self, mock_litellm, mock_decision, mock_votes):
        """Test summarize_decision handles empty API response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.summarize_decision(mock_decision, mock_votes)
        
        assert result == "Unable to generate summary"
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_suggest_next_steps_empty_response(self, mock_litellm, mock_decision, mock_votes):
        """Test suggest_next_steps handles empty API response."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        result = client.suggest_next_steps(mock_decision, mock_votes)
        
        assert result == "Unable to generate suggestions"
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_uninitialized_client_summarize(self, mock_litellm, mock_decision, mock_votes):
        """Test summarize_decision when client is not initialized."""
        client = AIClient()
        client.initialized = False
        
        result = client.summarize_decision(mock_decision, mock_votes)
        
        assert result is None
        mock_litellm.completion.assert_not_called()
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_uninitialized_client_suggest(self, mock_litellm, mock_decision, mock_votes):
        """Test suggest_next_steps when client is not initialized."""
        client = AIClient()
        client.initialized = False
        
        result = client.suggest_next_steps(mock_decision, mock_votes)
        
        assert result is None
        mock_litellm.completion.assert_not_called()
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_prompt_structure_summarize(self, mock_litellm, mock_decision, mock_votes):
        """Test that summarize_decision sends correct prompt structure."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        client.summarize_decision(mock_decision, mock_votes)
        
        call_args = mock_litellm.completion.call_args
        messages = call_args.kwargs['messages']
        
        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        assert 'content' in messages[0]
        assert isinstance(messages[0]['content'], str)
        
        # Verify prompt contains decision details
        prompt = messages[0]['content']
        assert "Should we deploy the new feature?" in prompt
        assert "pending" in prompt
        assert "2/5" in prompt  # approval_count/group_size_at_creation
        assert call_args.kwargs['model'] == 'openrouter/google/gemini-2.5-flash-lite'
    
    @patch('app.ai.ai_client.litellm')
    @patch('app.ai.ai_client.config.OPEN_ROUTER_API_KEY', 'test-api-key')
    def test_prompt_structure_suggest(self, mock_litellm, mock_decision, mock_votes):
        """Test that suggest_next_steps sends correct prompt structure."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_litellm.completion.return_value = mock_response
        
        client = AIClient()
        client.suggest_next_steps(mock_decision, mock_votes)
        
        call_args = mock_litellm.completion.call_args
        messages = call_args.kwargs['messages']
        
        assert isinstance(messages, list)
        assert len(messages) == 1
        assert messages[0]['role'] == 'user'
        
        # Verify prompt contains decision and vote details
        prompt = messages[0]['content']
        assert "Should we deploy the new feature?" in prompt
        assert "Alice" in prompt
        assert "Bob" in prompt
        assert "Charlie" in prompt


# Integration test (only runs if OPEN_ROUTER_API_KEY is set)
class TestAIClientIntegration:
    """Integration tests for real OpenRouter API calls."""
    
    @pytest.mark.skipif(
        not os.getenv('OPEN_ROUTER_API_KEY'),
        reason="OPEN_ROUTER_API_KEY not set in environment"
    )
    def test_real_api_call_summarize(self, mock_decision, mock_votes):
        """Integration test: Real API call to OpenRouter for summarization."""
        try:
            import litellm
        except ImportError:
            pytest.skip("litellm not installed")
        
        client = AIClient()
        
        if not client.initialized:
            pytest.skip("AI client not initialized - check API key")
        
        result = client.summarize_decision(mock_decision, mock_votes)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Unable to generate summary" not in result or result != "Unable to generate summary"
    
    @pytest.mark.skipif(
        not os.getenv('OPEN_ROUTER_API_KEY'),
        reason="OPEN_ROUTER_API_KEY not set in environment"
    )
    def test_real_api_call_suggest(self, mock_decision, mock_votes):
        """Integration test: Real API call to OpenRouter for suggestions."""
        try:
            import litellm
        except ImportError:
            pytest.skip("litellm not installed")
        
        client = AIClient()
        
        if not client.initialized:
            pytest.skip("AI client not initialized - check API key")
        
        result = client.suggest_next_steps(mock_decision, mock_votes)
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert "Unable to generate suggestions" not in result or result != "Unable to generate suggestions"
