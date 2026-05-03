from pipelines.graph.review_graph import graph

USERQUERY = "Is Sankalp in Udaipur really a good place?"


def main():
    
    final_summary = graph.invoke({
        "user_query": USERQUERY,
        "no_info": False,
        "no_reviews": False,
    })

    if final_summary["no_info"]:
        print("No place name and location found in the query.")
        return
    elif final_summary["no_reviews"]:
        print("No reviews found in any of the sources.")

    summary = final_summary["summary"]
    print(f"[Main] Gemini cooked this output: {summary}")

if __name__ == "__main__":
    main()