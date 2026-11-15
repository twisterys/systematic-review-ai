"""
Author : Yassir SAMADI
CLI Entry Point for the Multi-Agent Systematic Review Pipeline.
Usage:
    python main.py --topic "Cognitive Multi-Agent Ecosystems for Autonomous Talent Marketplaces"
"""

import argparse
import os
import json
from src.graph import SystematicReviewPipeline
from src.evaluation import evaluate_pipeline_run


def main():
    parser = argparse.ArgumentParser(description="Autonomous Systematic Review AI Pipeline (PRISMA 2020)")
    parser.add_argument(
        "--topic",
        type=str,
        default="Cognitive Multi-Agent Ecosystems for Autonomous Talent Marketplaces",
        help="Research topic for systematic review"
    )
    parser.add_argument(
        "--question",
        type=str,
        default="How do decentralized cognitive multi-agent architectures optimize talent matching and negotiation in autonomous talent marketplaces?",
        help="Primary research question"
    )
    parser.add_argument(
        "--outdir",
        type=str,
        default="./output",
        help="Directory to save generated outputs"
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print("=" * 80)
    print("🚀 LAUNCHING AUTONOMOUS SYSTEMATIC REVIEW PIPELINE (PRISMA 2020)")
    print(f"Topic: {args.topic}")
    print(f"Question: {args.question}")
    print("=" * 80)

    def print_callback(desc, pct, state):
        print(f"[{pct:3d}%] {desc}")

    pipeline = SystematicReviewPipeline()
    state = pipeline.run_full_pipeline(
        topic=args.topic,
        question=args.question,
        callback=print_callback
    )

    # Save outputs
    clean_topic = args.topic[:35].replace(" ", "_").lower()
    report_file = os.path.join(args.outdir, f"systematic_review_{clean_topic}.md")
    state_file = os.path.join(args.outdir, f"systematic_review_{clean_topic}_state.json")
    eval_file = os.path.join(args.outdir, f"systematic_review_{clean_topic}_eval.json")

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(state.get("final_report_markdown", ""))

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, default=str)

    eval_results = evaluate_pipeline_run(state)
    with open(eval_file, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print("\n" + "=" * 80)
    print("✅ SYSTEMATIC REVIEW PIPELINE COMPLETED")
    print(f"📄 Manuscript Report: {report_file}")
    print(f"📦 Full State JSON:   {state_file}")
    print(f"📈 Evaluation Metrics: {eval_file}")
    print("=" * 80)
    print(f"Identified Studies: {state.get('prisma_counts', {}).get('total_identified', 0)}")
    print(f"Deduplicated:       {len(state.get('deduplicated_studies', []))}")
    print(f"Included in Review: {state.get('prisma_counts', {}).get('final_included', 0)}")
    print(f"PRISMA Compliance:  {state.get('prisma_checklist_report', {}).get('score_percentage', 0)}%")
    print(f"Time Savings:       {eval_results.get('time_savings_percentage')} vs. manual review")
    print("=" * 80)


if __name__ == "__main__":
    main()
