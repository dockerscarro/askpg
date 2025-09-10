Here is the updated Python code to add search results display with highlighted matches:

from streamlit import code

def highlight_query_terms(text, query):
    words = query.split()
    for word in words:
        text = text.replace(word, f'<mark>{word}</mark>')
    return text

def display_search_results(results, query):
    if not results:
        st.info("No results found")
        return

    st.markdown(f"### Top {len(results)} Results")
    for i, result in enumerate(results, 1):
        highlighted_result = highlight_query_terms(result, query)
        st.markdown(f"{i}. {highlighted_result}", unsafe_allow_html=True)

if search_clicked and query and st.session_state.get("indexed"):
    with st.spinner("🔍 Searching logs..."):
        results = qdrant_search(query)
        display_search_results(results, query)

This code adds a new function `highlight_query_terms` that highlights the query terms in the text by wrapping them in `<mark>` HTML tags. The `display_search_results` function is used to display the search results with the query terms highlighted. The `unsafe_allow_html=True` parameter is passed to `st.markdown` to allow the use of HTML tags in the text. The call to `qdrant_search` is updated to store the results in a variable, which is then passed to `display_search_results` to display the results.