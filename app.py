import streamlit as st
import requests
import re
from difflib import SequenceMatcher

# Page configuration
st.set_page_config(
    page_title="Mr Eyobed's Auto Grader",
    page_icon="📝",
    layout="wide"
)

# Header
st.title("📝 Mr Eyobed's Auto Grader")
st.markdown("### *\"Do things genuinely\"*")
st.markdown("---")

# Reference code
REFERENCE_CODE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Bootstrap Spacing Demo</title>
  <!-- Bootstrap CDN -->
  <link 
    href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" 
    rel="stylesheet">
</head>
<body>
  <div class="container mt-4">
    <h2 class="mb-4">Bootstrap Spacing Classes</h2>
    <!-- Margin all sides -->
    <div class="m-3 bg-light border p-2">
      m-3 (Margin on all sides)
    </div>
    <!-- Margin top only -->
    <div class="mt-4 bg-light border p-2">
      mt-4 (Margin top only)
    </div>
    <!-- Margin bottom only -->
    <div class="mb-2 bg-light border p-2">
      mb-2 (Margin bottom only)
    </div>
    <!-- Padding all sides -->
    <div class="p-3 bg-primary text-white mb-3">
      p-3 (Padding on all sides)
    </div>
    <!-- Padding top only -->
    <div class="pt-5 bg-success text-white">
      pt-5 (Padding top only)
    </div>
  </div>
  <!-- Bootstrap JS -->
  <script 
    src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js">
  </script>
</body>
</html>"""

def fetch_github_file(github_url):
    """Fetch index.html from GitHub repository"""
    try:
        # Convert GitHub URL to raw content URL
        if "github.com" in github_url:
            # Handle different GitHub URL formats
            github_url = github_url.replace("github.com", "raw.githubusercontent.com")
            github_url = github_url.replace("/blob/", "/")
            
            # Ensure it points to index.html
            if not github_url.endswith("index.html"):
                if github_url.endswith("/"):
                    github_url += "index.html"
                else:
                    github_url += "/index.html"
        
        response = requests.get(github_url, timeout=10)
        response.raise_for_status()
        return response.text, None
    except requests.exceptions.RequestException as e:
        return None, f"Error fetching file: {str(e)}"

def grade_code(student_code):
    """Grade the student's code against reference"""
    criteria = {
        "DOCTYPE declaration": {
            "pattern": r"<!DOCTYPE html>",
            "points": 5,
            "type": "exact"
        },
        "HTML lang attribute": {
            "pattern": r'<html\s+lang="en">',
            "points": 5,
            "type": "regex"
        },
        "Character encoding (UTF-8)": {
            "pattern": r'<meta\s+charset="UTF-8">',
            "points": 5,
            "type": "regex"
        },
        "Viewport meta tag": {
            "pattern": r'<meta\s+name="viewport"',
            "points": 5,
            "type": "regex"
        },
        "Page title": {
            "pattern": r"<title>.*?</title>",
            "points": 5,
            "type": "regex"
        },
        "Bootstrap CSS CDN (v5.3.2)": {
            "pattern": r"bootstrap@5\.3\.2/dist/css/bootstrap\.min\.css",
            "points": 10,
            "type": "regex"
        },
        "Container class (mt-4)": {
            "pattern": r'class="container mt-4"',
            "points": 10,
            "type": "substring"
        },
        "Heading with mb-4": {
            "pattern": r'class="mb-4"',
            "points": 8,
            "type": "substring"
        },
        "Margin all sides (m-3)": {
            "pattern": r'class="m-3 bg-light border p-2"',
            "points": 10,
            "type": "substring"
        },
        "Margin top (mt-4)": {
            "pattern": r'class="mt-4 bg-light border p-2"',
            "points": 10,
            "type": "substring"
        },
        "Margin bottom (mb-2)": {
            "pattern": r'class="mb-2 bg-light border p-2"',
            "points": 10,
            "type": "substring"
        },
        "Padding all sides (p-3)": {
            "pattern": r'class="p-3 bg-primary text-white mb-3"',
            "points": 10,
            "type": "substring"
        },
        "Padding top (pt-5)": {
            "pattern": r'class="pt-5 bg-success text-white"',
            "points": 10,
            "type": "substring"
        },
        "Bootstrap JS CDN": {
            "pattern": r"bootstrap@5\.3\.2/dist/js/bootstrap\.bundle\.min\.js",
            "points": 7,
            "type": "regex"
        }
    }
    
    results = []
    total_score = 0
    max_score = sum(c["points"] for c in criteria.values())
    
    for name, criterion in criteria.items():
        pattern = criterion["pattern"]
        points = criterion["points"]
        check_type = criterion["type"]
        
        if check_type == "exact":
            passed = pattern in student_code
        elif check_type == "regex":
            passed = bool(re.search(pattern, student_code, re.IGNORECASE))
        else:  # substring
            passed = pattern in student_code
        
        if passed:
            total_score += points
            status = "✅"
        else:
            status = "❌"
        
        results.append({
            "criterion": name,
            "status": status,
            "points": points,
            "passed": passed
        })
    
    percentage = (total_score / max_score) * 100
    
    return results, total_score, max_score, percentage

def get_letter_grade(percentage):
    """Convert percentage to letter grade"""
    if percentage >= 90:
        return "A"
    elif percentage >= 80:
        return "B"
    elif percentage >= 70:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"

def generate_suggestions(results):
    """Generate suggestions based on failed criteria"""
    suggestions = []
    
    for result in results:
        if not result["passed"]:
            criterion = result["criterion"]
            
            if "DOCTYPE" in criterion:
                suggestions.append("• Add `<!DOCTYPE html>` at the very beginning of your HTML file")
            elif "lang attribute" in criterion:
                suggestions.append("• Ensure your `<html>` tag includes `lang=\"en\"`")
            elif "Character encoding" in criterion:
                suggestions.append("• Add `<meta charset=\"UTF-8\">` in the `<head>` section")
            elif "Viewport" in criterion:
                suggestions.append("• Include viewport meta tag: `<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">`")
            elif "title" in criterion:
                suggestions.append("• Add a `<title>` tag in the `<head>` section")
            elif "Bootstrap CSS" in criterion:
                suggestions.append("• Link Bootstrap 5.3.2 CSS from CDN in the `<head>` section")
            elif "Container" in criterion:
                suggestions.append("• Use `class=\"container mt-4\"` for the main container div")
            elif "Heading" in criterion:
                suggestions.append("• Add `class=\"mb-4\"` to your `<h2>` heading")
            elif "m-3" in criterion:
                suggestions.append("• Create a div with `class=\"m-3 bg-light border p-2\"` for margin all sides demo")
            elif "mt-4" in criterion:
                suggestions.append("• Create a div with `class=\"mt-4 bg-light border p-2\"` for margin top demo")
            elif "mb-2" in criterion:
                suggestions.append("• Create a div with `class=\"mb-2 bg-light border p-2\"` for margin bottom demo")
            elif "p-3" in criterion:
                suggestions.append("• Create a div with `class=\"p-3 bg-primary text-white mb-3\"` for padding all sides demo")
            elif "pt-5" in criterion:
                suggestions.append("• Create a div with `class=\"pt-5 bg-success text-white\"` for padding top demo")
            elif "Bootstrap JS" in criterion:
                suggestions.append("• Include Bootstrap 5.3.2 JS bundle from CDN before closing `</body>` tag")
    
    return suggestions

# Input form
col1, col2 = st.columns(2)

with col1:
    student_name = st.text_input("👤 Student Name", placeholder="Enter your name")

with col2:
    github_url = st.text_input("🔗 GitHub Repository URL", placeholder="https://github.com/username/repo/blob/main/index.html")

if st.button("🎯 Grade My Assignment", type="primary"):
    if not student_name:
        st.error("⚠️ Please enter your name")
    elif not github_url:
        st.error("⚠️ Please enter your GitHub URL")
    else:
        with st.spinner("Fetching and grading your code..."):
            student_code, error = fetch_github_file(github_url)
            
            if error:
                st.error(error)
                st.info("💡 **Tips for correct URL format:**")
                st.markdown("""
                - Make sure the URL points to your `index.html` file
                - Example: `https://github.com/username/repository/blob/main/index.html`
                - Or: `https://raw.githubusercontent.com/username/repository/main/index.html`
                """)
            else:
                # Grade the code
                results, total_score, max_score, percentage = grade_code(student_code)
                letter_grade = get_letter_grade(percentage)
                
                # Display results
                st.success(f"✅ Successfully graded {student_name}'s assignment!")
                st.markdown("---")
                
                # Score summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Score", f"{total_score}/{max_score}")
                with col2:
                    st.metric("Percentage", f"{percentage:.1f}%")
                with col3:
                    st.metric("Grade", letter_grade)
                
                # Detailed results
                st.markdown("### 📊 Detailed Grading Results")
                
                for result in results:
                    with st.expander(f"{result['status']} {result['criterion']} ({result['points']} points)"):
                        if result['passed']:
                            st.success(f"✅ Correct! You earned {result['points']} points")
                        else:
                            st.error(f"❌ Missing or incorrect. 0/{result['points']} points")
                
                # Suggestions
                suggestions = generate_suggestions(results)
                if suggestions:
                    st.markdown("### 💡 Suggestions for Improvement")
                    for suggestion in suggestions:
                        st.markdown(suggestion)
                else:
                    st.success("🎉 Perfect! Your code matches all criteria!")
                
                # Code comparison
                st.markdown("### 📝 Code Comparison")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Your Code:**")
                    st.code(student_code, language="html")
                
                with col2:
                    st.markdown("**Reference Code:**")
                    st.code(REFERENCE_CODE, language="html")

# Footer
st.markdown("---")
st.markdown("*Made with ❤️ by Mr Eyobed | Remember: Do things genuinely!*")