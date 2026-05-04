# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from core.config import GEMINI_TOKEN
from langchain_openai import ChatOpenAI
from core.config import OPEN_AI_API


# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     google_api_key=GEMINI_TOKEN,
#     temperature=0.1
# )

llm = ChatOpenAI(
    model="openai/gpt-oss-120b:free",
    api_key=OPEN_AI_API,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2
)


def format_reviews_for_prompt(reviews: list[dict]) -> str:
    formatted_str = ""
    for review_cnt, review in enumerate(reviews, start=1):

        author = review.get('author')
        rating = review.get('rating')
        text = review.get('text')

        formatted_str += (f'{review_cnt}. {author} says "{text}" and gave a rating of {rating}\n')

    print(f"[REVIEW PIPELINE] Final review string for prompt prepared.")
    return formatted_str


# for extracting place name and location from the user query.
def extract_place_info(user_query: str) -> dict:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template= """
        You are a information extraction system

        Task:
        Extract a single place or business name and its location from the user query.

        Rules:
        - Return ONLY a valid JSON object. No explanation, no extra text, no formatting, just the JSON.
        - JSON keys MUST be exactly 'place_name', 'location'.
        - If multiple places/businesses or locations are mentioned, return the most relevant one.
        - If no place name is found, set 'place_name' to "".
        - If no location is found, set 'location' to "".
        - Keep values concise and clean (no extra words like "near", "around", "in", etc.).
        - Do not infer missing information beyond what is explicitly stated.

        Examples:
        Input: "Reviews about Starbucks in New York"
        Output: {{ "place_name": "Starbucks", "location": "New York" }}

        Input: "How's the vibe at Nithya Amirtham?"
        Output: {{ "place_name": "Nithya Amirtham", "location": "" }}

        Input: "Find me the best pizza place nearby"
        Output: {{ "place_name": "", "location": "" }}

        Now extract the information from this query: 
        {user_query}
        """
    )


    chain = prompt | llm | JsonOutputParser()
    print("[REVIEW PIPELINE] Extraction chain ready")


    place_info: dict = chain.invoke({"user_query" : user_query})
    print(f"[REVIEW PIPELINE] Extraction chain invoked. Place info ready: {place_info}")

    return place_info


# for summarizing the reviews
def summarize_reviews(place_name: str, location: str, reviews: list[str]) -> str:
    reviews = format_reviews_for_prompt(reviews)

    prompt = PromptTemplate(
        input_variables=["place_name", "location", "reviews"],
        template="""
        You are a professional review summarizer.
        
        Task:
        Summarize the reviews for {place_name} in {location} into a single, 
        natural and informative paragraph. Cover the overall experience, 
        standout positives(pros), notable negatives(cons), and who this place is best suited for.

        STRICT RULE: Only use information explicitly mentioned in the reviews.
        Do not use any prior knowledge about this place.

        These are the Reviews:
        {reviews}
        
        Output:
        Return ONLY the paragraph.
        First a normal conversational statement acknowledging the request.
        For example: "Sure here is the overall summary of the reviews for {place_name}.
        Not this exact statement but similar to this. 
        Then the summary paragraph formatted as headings, bullet points.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    print("[REVIEW PIPELINE] Summarize chain ready")


    summarized_reviews: str = chain.invoke({"place_name": place_name, "location" : location, "reviews": reviews})
    print("[REVIEW PIPELINE] Summarize chain invoked. Reviews Summarized")

    return summarized_reviews


# for detecting the intent of user
def detect_intent(user_query: str, conversation_history: str) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query", "conversation_history"],
        template="""
        You are an intent detection system.

        Conversation history:
        {conversation_history}

        Latest user query: {user_query}

        Your job:
        First, check if the latest query refers to anything in the conversation history 
        (including pronouns like "it", "there", "that place", "this place").

        If the query refers to a place or business or anything related to asking about the place like the price, food or any amenitie mentioned in the conversation history:
        → Return a short intent phrase (2-5 words) describing what the user wants to know.
        Examples:
        - "overall quality skeptical"
        - "food quality"
        - "family suitability"
        - "value for money"
        - "ambience and vibe"

        If the query has absolutely NO connection to the conversation history 
        AND is purely casual small talk (like "how are you", "what's up", "thanks"):
        → Return exactly "contextless"

        IMPORTANT: Queries like "is it really that good?", "what about the food there?", 
        "is that place worth it?" are ALWAYS referring to the conversation history.
        Never mark these as contextless.

        Return ONLY the intent phrase or "contextless". Nothing else.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    print("[REVIEW PIPELINE] Intent Detection chain ready")
    
    intent = chain.invoke({"user_query": user_query, "conversation_history": conversation_history})
    print(f"[REVIEW PIPELINE] Intent Determined: {intent}")

    return intent


# for replying to normal conversation of the user
def normal_conversation(user_query: str) -> str:
    prompt = PromptTemplate(
        input_variables=["user_query"],
        template="""
        You are a very good and great talker.
        
        Task:
        Reply to the query of user as a friend and a buddy enthusiastically and conversationally and in a very friendly way and tone.

        User query: {user_query}

        Output:
        A very normal basic conversational tone sentence and nothing else. No keywords, no buzzwords. Just the string.
        """
    )
    
    chain = prompt | llm | StrOutputParser()
    print("[REVIEW PIPELINE] Conversation chain ready")
    
    response = chain.invoke({"user_query": user_query})
    print(f"[REVIEW PIPELINE] Conversation Complete")

    return response


# Only for follow ups
def rewrite_on_intent(place_name: str, intent: str, relevant_reviews: list[str], conversation_history: str) -> str:
    formatted_reviews = "\n".join(f"{i}. {r}" for i, r in enumerate(relevant_reviews, start=1))

    prompt = PromptTemplate(
        input_variables=["place_name", "intent", "reviews", "conversation_history"],
        template="""
        You are a helpful assistant answering follow-up questions about a place.

        Place:
        {place_name}
        
        User's intent:
        {intent}

        Conversation so far:
        {conversation_history}

        Most relevant reviews for this intent:
        {reviews}
        
        Task:
        Write a focused, natural paragraph that directly addresses the user's intent.
        Base your response ONLY on the reviews provided.
        Match the tone to the intent — if skeptical, be honest about negatives.
        If asking about a specific aspect, focus only on that aspect and respond accordingly.
        
        Keep in mind:
        The paragraph should be conversational while also accounting the user's intent.
        For example: If the user's intent is somewhat skeptical about the place being good.
        Then respond like: "Yeahhh! that place is actually good(or bad based on the relevant reviews given).
        Like just be generally conversational like a normal human being answering to a followup asked to him/her.
        Similarly for any type of intentions, just refer the relevant reviews and based on the intent and relevant reviews, repond.

        Output:
        Return ONLY the paragraph.
        """
    )

    chain = prompt | llm | StrOutputParser()
    print("[REVIEW PIPELINE] Rewrite chain ready")

    follow_up_response = chain.invoke({"place_name": place_name, "intent": intent, "reviews": formatted_reviews, "conversation_history": conversation_history})
    print(f"[REVIEW PIPELINE] Rewrite chain invoked. Follow up response generated")

    return follow_up_response