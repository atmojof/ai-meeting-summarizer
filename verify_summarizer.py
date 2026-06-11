import sys
from utils.summarizer_engine import TranscriptParser, MetricsEngine, SummaryCompiler

def run_tests():
    print("==================================================")
    print("Running Meeting Summarizer Engine Validation Tests")
    print("==================================================")
    
    passed_tests = 0
    total_tests = 0
    
    def assert_test(condition, message):
        nonlocal passed_tests, total_tests
        total_tests += 1
        if condition:
            print(f"[PASS] {message}")
            passed_tests += 1
        else:
            print(f"[FAIL] {message}")
            sys.exit(1)

    # Test 1: Transcript parsing structure
    test_text = (
        "Sarah: Welcome team, let's review the sprint.\n"
        "John: I will deploy the hotfix for the database API this afternoon.\n"
        "Emma: Great. Sarah, can you review the repository code?"
    )
    
    parsed = TranscriptParser.parse(test_text)
    assert_test(len(parsed["dialogues"]) == 3, f"Parser should extract exactly 3 dialogue turns (extracted: {len(parsed['dialogues'])})")
    assert_test("Sarah" in parsed["speaker_words"] and "John" in parsed["speaker_words"] and "Emma" in parsed["speaker_words"], "Speakers must be extracted correctly by name")
    
    # Test 2: Speaker word count shares summing to 100%
    shares = parsed["speaker_shares"]
    shares_sum = round(sum(shares.values()), 0)
    assert_test(shares_sum == 100.0, f"Speaker share percentages must sum to 100.0% (sum: {shares_sum}%)")

    # Test 3: Topic weights matching
    # 'database API' (Tech), 'sprint' (Operations)
    topics = MetricsEngine.analyze_topic_weights(parsed["dialogues"])
    assert_test(topics["Tech"] > 0.0, f"Tech topic weight should be flagged positive (calculated: {topics['Tech']}%)")
    assert_test(topics["Operations"] > 0.0, f"Operations topic weight should be flagged positive (calculated: {topics['Operations']}%)")

    # Test 4: Sentiment valence scoring
    pos_dialogue = [{"speaker": "John", "text": "great perfect solved success thanks"}]
    neg_dialogue = [{"speaker": "John", "text": "disagree error failed blocker problem"}]
    
    pos_sent = MetricsEngine.analyze_sentiment_timeline(pos_dialogue)[0]
    neg_sent = MetricsEngine.analyze_sentiment_timeline(neg_dialogue)[0]
    
    assert_test(pos_sent > 0.0, f"Positive dialogues should score positive sentiment (calculated: {pos_sent})")
    assert_test(neg_sent < 0.0, f"Negative dialogues should score negative sentiment (calculated: {neg_sent})")

    # Test 5: Summary & Action Items Extraction
    speaker_names = list(shares.keys())
    summary = SummaryCompiler.generate_summary(parsed["dialogues"], speaker_names)
    
    assert_test(len(summary["executive_summary"]) > 0, "Executive summary description should be generated")
    
    # 'John: I will deploy the hotfix...' -> Action item owner: John
    actions = summary["action_items"]
    assert_test(any(item["owner"] == "John" for item in actions), "Action items parser should capture John's 'I will deploy...' item")
    
    print("==================================================")
    print(f"All {passed_tests}/{total_tests} Summarizer tests PASSED successfully!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
