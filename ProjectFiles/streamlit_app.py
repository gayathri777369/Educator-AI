"""
EducatorAI - Streamlit Application
A simplified web interface for educational content generation
"""
import streamlit as st
import asyncio
import time
from typing import Dict, Any, Optional
import random


# Configure page
st.set_page_config(
    page_title="EducatorAI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Educational templates (same as FastAPI version)
EDUCATIONAL_TEMPLATES = {
    "explanation": """Here's a detailed explanation of {topic}:

{topic} is an important concept that involves multiple aspects. Let me break it down:

1. Definition: {topic} refers to...
2. Key Components: The main elements include...
3. How it Works: The process involves...
4. Examples: Common examples include...
5. Importance: This is significant because...

Understanding {topic} is crucial for building foundational knowledge in this area.""",

    "summary": """Summary of {topic}:

• Main Points:
  - Key aspect 1 of {topic}
  - Important feature 2
  - Critical element 3

• Context: {topic} is relevant in multiple fields

• Applications: Used in various practical scenarios

• Conclusion: {topic} represents a fundamental concept worth understanding thoroughly.""",

    "quiz": """Quiz: {topic}

1. Multiple Choice:
What is the primary characteristic of {topic}?
a) Option A
b) Option B
c) Option C
d) Option D

2. True/False:
{topic} is always applicable in all contexts. (True/False)

3. Short Answer:
Explain one key benefit of understanding {topic}.

4. Fill in the blank:
The most important aspect of {topic} is ________.

Answer Key:
1. c) Option C
2. False
3. Sample answer: Understanding helps with...
4. [Key concept]""",

    "lesson": """Lesson Plan: {topic}

Objective: Students will understand the key concepts of {topic}

Materials Needed:
- Whiteboard/projector
- Handouts
- Interactive materials

Lesson Structure:

1. Introduction (10 minutes)
   - Hook: Engaging question about {topic}
   - Learning objectives

2. Main Content (25 minutes)
   - Explain core concepts
   - Provide examples
   - Interactive discussion

3. Practice Activity (10 minutes)
   - Hands-on exercise
   - Group work

4. Conclusion (5 minutes)
   - Recap key points
   - Preview next lesson

Assessment: Quiz on main concepts
Homework: Research additional examples""",

    "example": """Examples of {topic}:

1. Real-world Example 1:
   In everyday life, {topic} can be seen when...
   This demonstrates how the concept applies practically.

2. Academic Example 2:
   In academic settings, {topic} is evident in...
   This shows the theoretical application.

3. Historical Example 3:
   Throughout history, {topic} has been important in...
   This provides historical context.

4. Modern Example 4:
   In today's world, {topic} is relevant in...
   This shows current relevance.

These examples illustrate the versatility and importance of understanding {topic}.""",

    "definition": """Definition: {topic}

{topic} is defined as...

Key Characteristics:
• Primary feature 1
• Important aspect 2
• Essential element 3

Context and Usage:
{topic} is commonly used in the context of... It's particularly relevant when discussing...

Related Terms:
- Synonym 1
- Related concept 2
- Associated term 3

Significance:
Understanding {topic} is important because it forms the foundation for... and helps in comprehending..."""
}

def extract_topic(prompt: str) -> str:
    """Extract the main topic from the prompt"""
    words = prompt.lower().split()
    
    # Remove common question words and prepositions
    stop_words = {'what', 'how', 'why', 'where', 'when', 'who', 'is', 'are', 'the', 'a', 'an', 'about', 'of', 'for', 'in', 'on', 'to', 'with'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    if filtered_words:
        return ' '.join(filtered_words[:3])  # Take first 3 meaningful words
    else:
        return prompt[:50]  # Fallback to first 50 characters

def generate_educational_content(
    prompt: str,
    content_type: str,
    context: Optional[str] = None,
    max_length: int = 512,
    temperature: float = 0.7
) -> Dict[str, Any]:
    """Generate educational content using templates"""
    
    # Simulate processing time
    time.sleep(random.uniform(1.5, 3.0))
    
    # Get template
    template = EDUCATIONAL_TEMPLATES.get(content_type, EDUCATIONAL_TEMPLATES['explanation'])
    
    # Extract topic
    topic = extract_topic(prompt)
    
    # Generate content
    content = template.replace('{topic}', topic)
    
    # Add context if provided
    if context:
        content += f"\n\nAdditional Context:\n{context}"
    
    # Add variety based on prompt
    if 'beginner' in prompt.lower() or 'basic' in prompt.lower():
        content += f"\n\nNote: This explanation is tailored for beginners learning about {topic}."
    elif 'advanced' in prompt.lower() or 'detailed' in prompt.lower():
        content += f"\n\nAdvanced Note: For deeper understanding of {topic}, consider exploring related research and applications."
    
    return {
        "generated_text": content,
        "topic": topic,
        "content_type": content_type,
        "parameters": {
            "max_length": max_length,
            "temperature": temperature
        }
    }

def main():
    """Main Streamlit application"""
    
    # Header
    st.title("🎓 EducatorAI")
    st.markdown("**Generate Educational Content with AI**")
    st.markdown("---")
    
    # Sidebar for settings
    st.sidebar.header("⚙️ Settings")
    
    # Content type selection
    content_type = st.sidebar.selectbox(
        "📝 Content Type",
        options=["explanation", "summary", "quiz", "lesson", "example", "definition"],
        index=0,
        help="Select the type of educational content to generate"
    )
    
    # Advanced settings
    st.sidebar.subheader("🔧 Advanced Settings")
    max_length = st.sidebar.slider("📏 Max Length", 50, 1000, 512, 50)
    temperature = st.sidebar.slider("🌡️ Creativity", 0.1, 2.0, 0.7, 0.1)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input")
        
        # Main prompt input
        prompt = st.text_area(
            "What would you like to learn about?",
            placeholder="Enter your educational topic or question here...",
            height=100,
            help="Enter the topic you want to generate educational content about"
        )
        
        # Context input
        context = st.text_area(
            "Additional Context (Optional)",
            placeholder="Provide any additional context, target audience, or specific requirements...",
            height=80,
            help="Optional context to customize the generated content"
        )
        
        # Generate button
        generate_clicked = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    
    with col2:
        st.header("📖 Generated Content")
        
        # Initialize session state
        if 'generated_content' not in st.session_state:
            st.session_state.generated_content = None
        if 'generation_time' not in st.session_state:
            st.session_state.generation_time = 0
        
        # Generate content when button clicked
        if generate_clicked:
            if not prompt.strip():
                st.error("Please enter a topic or question.")
            else:
                with st.spinner("Generating educational content..."):
                    start_time = time.time()
                    
                    try:
                        result = generate_educational_content(
                            prompt=prompt,
                            content_type=content_type,
                            context=context,
                            max_length=max_length,
                            temperature=temperature
                        )
                        
                        st.session_state.generated_content = result
                        st.session_state.generation_time = time.time() - start_time
                        
                        st.success(f"Content generated successfully in {st.session_state.generation_time:.2f}s!")
                        
                    except Exception as e:
                        st.error(f"Error generating content: {str(e)}")
        
        # Display generated content
        if st.session_state.generated_content:
            result = st.session_state.generated_content
            
            # Content metadata
            col_meta1, col_meta2, col_meta3 = st.columns(3)
            with col_meta1:
                st.metric("Content Type", result['content_type'].title())
            with col_meta2:
                st.metric("Topic", result['topic'])
            with col_meta3:
                st.metric("Generation Time", f"{st.session_state.generation_time:.2f}s")
            
            # Generated text
            st.text_area(
                "Generated Content",
                value=result['generated_text'],
                height=400,
                disabled=True
            )
            
            # Action buttons
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                if st.button("📋 Copy to Clipboard"):
                    # Note: Streamlit doesn't have native clipboard support
                    st.info("Content is ready to copy from the text area above!")
            
            with col_action2:
                # Download button
                st.download_button(
                    label="💾 Download as Text",
                    data=result['generated_text'],
                    file_name=f"educatorai_{result['content_type']}_{int(time.time())}.txt",
                    mime="text/plain"
                )
            
            with col_action3:
                if st.button("🔄 Generate New"):
                    st.session_state.generated_content = None
                    st.rerun()
        
        else:
            # Empty state
            st.info("👆 Enter a topic above and click 'Generate Content' to get started.")
    
    # Footer
    st.markdown("---")
    col_footer1, col_footer2, col_footer3 = st.columns([1, 2, 1])
    
    with col_footer2:
        st.markdown(
            "<div style='text-align: center; color: #666;'>"
            "© 2025 EducatorAI - Powered by Educational Templates"
            "</div>", 
            unsafe_allow_html=True
        )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.subheader("ℹ️ About")
    st.sidebar.info(
        "EducatorAI generates structured educational content across multiple formats. "
        "Perfect for teachers, students, and content creators."
    )
    
    st.sidebar.subheader("🎯 Content Types")
    st.sidebar.markdown("""
    - **Explanation**: Detailed breakdowns with examples
    - **Summary**: Concise key points overview
    - **Quiz**: Interactive questions and answers
    - **Lesson**: Structured teaching plans
    - **Example**: Real-world applications
    - **Definition**: Clear terminology explanations
    """)

if __name__ == "__main__":
    main()