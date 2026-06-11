import re
from typing import Dict, Any, List

class TranscriptParser:
    @classmethod
    def parse(cls, raw_text: str) -> Dict[str, Any]:
        """
        Parses transcripts structured as:
        [Speaker Name]: Message
        Or:
        Speaker Name: Message
        """
        lines = raw_text.strip().split("\n")
        dialogues = []
        speaker_words = {}
        current_speaker = "Unknown"
        
        # Pattern to capture "[Speaker Name]:" or "Speaker Name:"
        pattern = re.compile(r"^\[?([A-Za-z0-9\s\-]+)\]?\s*:\s*(.*)$")
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            match = pattern.match(line_str)
            if match:
                speaker = match.group(1).strip()
                message = match.group(2).strip()
                current_speaker = speaker
                dialogues.append({"speaker": speaker, "text": message})
                
                # Count words
                words_count = len(message.split())
                speaker_words[speaker] = speaker_words.get(speaker, 0) + words_count
            else:
                # Continuation of previous speaker
                dialogues.append({"speaker": current_speaker, "text": line_str})
                words_count = len(line_str.split())
                speaker_words[current_speaker] = speaker_words.get(current_speaker, 0) + words_count
                
        total_words = sum(speaker_words.values()) or 1
        speaker_shares = {spk: round((cnt / total_words) * 100, 1) for spk, cnt in speaker_words.items()}
        
        return {
            "dialogues": dialogues,
            "speaker_words": speaker_words,
            "speaker_shares": speaker_shares,
            "total_words": total_words
        }


class MetricsEngine:
    POSITIVE_WORDS = {"agree", "great", "good", "perfect", "solved", "success", "achieved", "excellent", "yes", "clear", "support", "thanks", "done", "fine"}
    NEGATIVE_WORDS = {"disagree", "difficult", "error", "failed", "issue", "delay", "blocker", "problem", "risk", "no", "concern", "wrong", "cannot", "slow"}

    TOPICS = {
        "Tech": {"api", "code", "server", "database", "frontend", "backend", "bug", "deploy", "git", "docker", "aws", "testing", "platform", "endpoint", "architecture"},
        "Marketing": {"campaign", "ads", "brand", "growth", "lead", "social", "seo", "acquisition", "clicks", "conversion", "audience", "metrics", "newsletter"},
        "Finance": {"budget", "revenue", "cost", "sales", "billing", "invoice", "funding", "expenses", "financial", "pricing", "target", "spend"},
        "Operations": {"hiring", "onboarding", "culture", "recruiting", "sprint", "meeting", "agile", "workflow", "process", "planning", "schedule", "deadline", "retro"}
    }

    @classmethod
    def analyze_sentiment_timeline(cls, dialogues: List[Dict[str, str]]) -> List[float]:
        """
        Splits dialogue into 5 segments and estimates sentiment scores [-1.0 to 1.0].
        """
        if not dialogues:
            return [0.0] * 5
            
        # Segment dialogues into 5 buckets
        chunk_size = max(1, len(dialogues) // 5)
        timeline_scores = []
        
        for i in range(5):
            start = i * chunk_size
            end = len(dialogues) if i == 4 else (i + 1) * chunk_size
            chunk = dialogues[start:end]
            
            pos_cnt = 0
            neg_cnt = 0
            
            for item in chunk:
                text_words = [w.lower().strip(",.?!:;()\"") for w in item["text"].split()]
                for word in text_words:
                    if word in cls.POSITIVE_WORDS:
                        pos_cnt += 1
                    elif word in cls.NEGATIVE_WORDS:
                        neg_cnt += 1
                        
            denom = pos_cnt + neg_cnt
            score = round((pos_cnt - neg_cnt) / denom, 2) if denom > 0 else 0.0
            timeline_scores.append(score)
            
        return timeline_scores

    @classmethod
    def analyze_topic_weights(cls, dialogues: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Calculates density percentage weights of major topics.
        """
        counts = {topic: 0 for topic in cls.TOPICS}
        
        for item in dialogues:
            text_words = [w.lower().strip(",.?!:;()\"") for w in item["text"].split()]
            for word in text_words:
                for topic, word_set in cls.TOPICS.items():
                    if word in word_set:
                        counts[topic] += 1
                        
        total_counts = sum(counts.values()) or 1
        topic_weights = {topic: round((cnt / total_counts) * 100, 1) for topic, cnt in counts.items()}
        return topic_weights


class SummaryCompiler:
    @classmethod
    def generate_summary(cls, dialogues: List[Dict[str, str]], speaker_names: List[str]) -> Dict[str, Any]:
        """
        Compiles meeting recap: Executive Summary, Key Decisions, and Action Items.
        """
        # Formulate some rule-based extraction or mock fallback depending on dialogue keywords
        exec_summary = ""
        decisions = []
        action_items = []
        
        # Scanners for task patterns: e.g., "John to complete...", "I will deploy..."
        # Pattern 1: [SpeakerName] will/to [do something]
        # Pattern 2: I will [do something] (belongs to current speaker)
        # Pattern 3: Need to [do something] (belongs to "All")
        
        action_verbs = ["deploy", "fix", "review", "schedule", "update", "write", "check", "create", "send", "prepare", "test", "build", "research", "contact"]
        
        for i, item in enumerate(dialogues):
            speaker = item["speaker"]
            text = item["text"]
            text_lower = text.lower()
            
            # 1. Look for decision indicators
            if any(k in text_lower for k in ["decided to", "we decided", "we will go with", "decision is", "agree on", "agreed to"]):
                # Clean prefix for display
                clean_dec = text.replace("We decided to ", "").replace("We decided ", "").replace("decision is to ", "")
                decisions.append(f"Approved: {clean_dec}")
                
            # 2. Look for action item indicators
            # Direct "I will..."
            if "i will " in text_lower or "i'll " in text_lower:
                for verb in action_verbs:
                    idx = text_lower.find(f"i will {verb}")
                    if idx == -1:
                        idx = text_lower.find(f"i'll {verb}")
                    if idx != -1:
                        action_str = text[idx:].split(".")[0].strip()
                        # Set priority
                        priority = "High" if any(u in text_lower for u in ["urgent", "asap", "critical", "today"]) else "Medium"
                        action_items.append({
                            "action": action_str,
                            "owner": speaker,
                            "priority": priority,
                            "deadline": "End of Sprint"
                        })
                        break
                        
            # Direct "Name to..." or "Name will..."
            for other_speaker in speaker_names:
                # Avoid matching the current speaker saying "I"
                if other_speaker.lower() == speaker.lower():
                    continue
                match_will = re.search(rf"\b{re.escape(other_speaker.lower())}\s+(will|to|should)\s+(\w+.*?)(?:\.|$)", text_lower)
                if match_will:
                    action_part = match_will.group(2).strip()
                    # Clean up verb start
                    priority = "High" if any(u in text_lower for u in ["urgent", "asap", "critical", "today"]) else "Medium"
                    action_items.append({
                        "action": f"{action_part.capitalize()}",
                        "owner": other_speaker,
                        "priority": priority,
                        "deadline": "End of Week"
                    })
                    break
        
        # Deduplicate and cap list
        decisions = list(set(decisions))[:5]
        
        # Build default executive summary description if list is too small
        if dialogues:
            exec_summary = (
                f"The meeting covered discussions across {len(dialogues)} conversational exchanges. "
                f"The primary contributors were {', '.join(speaker_names[:3])}. "
                f"Discussion concentrated on resolving active timelines and clarifying assigned deliverables."
            )
        else:
            exec_summary = "Empty dialogue log submitted. No discussions parsed."
            
        # Add basic defaults if none parsed
        if not decisions:
            decisions = [
                "Agreed to schedule a follow-up session once task items are completed.",
                "Review sprint timelines at next sync meeting."
            ]
        if not action_items:
            action_items = [
                {"action": "Review parsed transcript logs", "owner": speaker_names[0] if speaker_names else "All", "priority": "Medium", "deadline": "End of Week"},
                {"action": "Setup meeting minutes recap distribution list", "owner": "All", "priority": "Low", "deadline": "Next Sync"}
            ]
            
        return {
            "executive_summary": exec_summary,
            "decisions": decisions,
            "action_items": action_items
        }
