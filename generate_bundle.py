#!/usr/bin/env python3
"""
Generate a single self-contained HTML file that users can open offline.
It embeds:
- payload JSON (per-user/case prefill and metadata)
- form definition (derived from your existing handover_app.forms)

Usage examples:
  python3 generate_bundle.py --form base_install \
      --out handover_base_install.html \
      --message "Fill out and download the JSON at the end"

  python3 generate_bundle.py --form onboard_customer \
      --prefill '{"customer_name":"ACME"}' \
      --out handover_onboard_customer.html

  python3 generate_bundle.py --form large_cluster --out handover_large_cluster.html

You can also pass a custom JSON schema via --form-json path.json if preferred.
"""
import argparse
import json
import pathlib
import sys
from typing import Any, Dict

REPO_ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATE_PATH = REPO_ROOT / "index.template.html"

# Load form definitions directly from file to avoid importing package __init__
import runpy
FORMS_PATH = REPO_ROOT / "handover_app" / "forms.py"
large_cluster_form_sections = None
large_cluster_stage_order = None
base_install_form_definition = None
onboard_customer_form_definition = None
onboard_supplier_form_definition = None

if FORMS_PATH.exists():
    try:
        ns = runpy.run_path(str(FORMS_PATH))
        large_cluster_form_sections = ns.get("large_cluster_form_sections")
        large_cluster_stage_order = ns.get("large_cluster_stage_order")
        base_install_form_definition = ns.get("base_install_form_definition")
        onboard_customer_form_definition = ns.get("onboard_customer_form_definition")
        onboard_supplier_form_definition = ns.get("onboard_supplier_form_definition")
    except Exception:
        pass


def to_unified_definition(kind: str) -> Dict[str, Any]:
    kind = kind.lower()
    if kind == "base_install" and base_install_form_definition:
        return base_install_form_definition
    if kind == "onboard_customer" and onboard_customer_form_definition:
        return onboard_customer_form_definition
    if kind == "onboard_supplier" and onboard_supplier_form_definition:
        return onboard_supplier_form_definition
    if kind == "large_cluster" and large_cluster_form_sections and large_cluster_stage_order:
        # Normalize to a structure the template understands: stages + stage_order
        return {
            "title": "Large Cluster",
            "stages": {k: large_cluster_form_sections[k] for k in large_cluster_stage_order},
            "stage_order": list(large_cluster_stage_order),
        }
    raise SystemExit(f"Unknown or unavailable form kind: {kind}")


def apply_portable_overrides(form_def: Dict[str, Any], kind: str) -> Dict[str, Any]:
    """Apply overrides to the form definition so the portable bundle has
    your custom behavior without editing upstream files.
    Currently implemented for base_install:
      - Component Overview: Component Type becomes a dropdown with
        Node, Switch, Router, OOB Management, and per-row extra fields
        depending on the selected type.
      - Append "Additional Links and Network Details" section with
        Notion/Netbox/Build/Config links and a Public IP Addresses table.
    """
    import copy
    kind = kind.lower()
    if kind != "base_install":
        return form_def

    fd = copy.deepcopy(form_def)
    sections = fd.get("sections", [])

    # 1) Update Component Overview dynamic table
    for sec in sections:
        for fld in sec.get("fields", []):
            if fld.get("name") == "component_overview" and fld.get("type") == "dynamic_table":
                fld["columns"] = [
                    {"name": "component_type", "label": "Component Type", "type": "select",
                     "options": ["Node", "Switch", "Router", "OOB Management"]},
                    {"name": "hostname", "label": "Hostname / Identifier", "type": "text"},
                    {"name": "ip_address", "label": "IP Address", "type": "text"},
                    {"name": "os_version", "label": "OS Version", "type": "text"},
                    {"name": "last_patch_date", "label": "Last Patch Date", "type": "text"},
                ]
                # per-row conditional extras
                fld["row_conditions"] = {
                    "by": "component_type",
                    "map": {
                        "Node": [
                            {"name": "gpu_make", "label": "GPU Make", "type": "text"},
                            {"name": "gpu_model", "label": "GPU Model", "type": "text"},
                            {"name": "driver_version", "label": "Driver Version", "type": "text"},
                        ],
                        "Switch": [
                            {"name": "make", "label": "Make", "type": "text"},
                            {"name": "model", "label": "Model", "type": "text"},
                        ],
                        "Router": [
                            {"name": "make", "label": "Make", "type": "text"},
                            {"name": "model", "label": "Model", "type": "text"},
                        ],
                    },
                }
                # Remove legacy options/placeholders if present
                fld.pop("options", None)
                fld.pop("placeholders", None)

    # 2) Transform Support Type to checkbox-based multiselect with conditional tiers
    for sec in sections:
      for i, fld in enumerate(sec.get("fields", [])):
        if fld.get("name") == "support_type":
          sec["fields"][i] = {
            "name": "support_type",
            "label": "Support Type",
            "type": "multiselect_conditional",
            "widget": "checkboxes",
            "options": ["None", "Basic Support", "Managed Services"],
            "conditions": {
              "Managed Services": [
                {"name": "managed_systems_administration", "label": "Managed Systems Administration", "type": "select", "options": ["Gold", "Silver", "Bronze"]},
                {"name": "managed_slurm", "label": "Managed Slurm", "type": "select", "options": ["None", "Gold", "Silver", "Bronze"]},
              ]
            }
          }

    # 3) Append Additional Links and Network Details section at the end
    extra_section = {
        "title": "Additional Links and Network Details",
        "fields": [
            {"name": "notion_links", "label": "Notion Links", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "link", "label": "Link", "type": "url"},
             ]},
            {"name": "netbox_links", "label": "Netbox Links", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "link", "label": "Link", "type": "url"},
             ]},
            {"name": "build_diagrams", "label": "Build Diagrams", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "link", "label": "Link", "type": "url"},
             ]},
            {"name": "build_files", "label": "Build Files", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "link", "label": "Link", "type": "url"},
             ]},
            {"name": "configuration_files", "label": "Configuration Files", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "link", "label": "Link", "type": "url"},
             ]},
            {"name": "public_ip_addresses", "label": "Public IP Addresses", "type": "dynamic_table",
             "columns": [
                 {"name": "description", "label": "Description", "type": "text"},
                 {"name": "ip_address", "label": "IP Address", "type": "text"},
                 {"name": "dns", "label": "DNS", "type": "text"},
                 {"name": "dns_config_location", "label": "DNS Config Location", "type": "text"},
             ]},
        ],
    }

    fd.setdefault("sections", []).append(extra_section)
    return fd


def main():
    ap = argparse.ArgumentParser(description="Generate portable handover HTML bundle")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--form", choices=[
        "base_install", "onboard_customer", "onboard_supplier", "large_cluster"
    ], help="Choose a built-in form from your codebase")
    group.add_argument("--form-json", help="Path to a custom form definition JSON file")

    ap.add_argument("--out", required=True, help="Output HTML file path")
    ap.add_argument("--message", help="Notice text displayed at the top", default="No internet required. Your data stays in this browser until you download it.")
    ap.add_argument("--prefill", help="JSON object string to prefill form fields", default="{}")
    ap.add_argument("--output-filename", help="Suggested downloaded filename for the result JSON", default="")
    args = ap.parse_args()

    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    # Build form definition
    if args.form_json:
        form_def = json.loads(pathlib.Path(args.form_json).read_text(encoding="utf-8"))
    else:
        form_def = to_unified_definition(args.form)
        # Apply overrides for portable bundle behavior
        form_def = apply_portable_overrides(form_def, args.form)

    # Payload
    try:
        prefill_obj = json.loads(args.prefill)
    except json.JSONDecodeError:
        raise SystemExit("--prefill must be a valid JSON object string")

    payload = {
        "message": args.message,
        "prefill": prefill_obj,
        "draftKey": f"handover_draft_{args.form_json or args.form}",
    }
    if args.output_filename:
        payload["outputFilename"] = args.output_filename

    # Inject JSON into template
    html = template.replace("__PAYLOAD__", json.dumps(payload, separators=(",", ":")))
    html = html.replace("__FORM_DEFINITION__", json.dumps(form_def, separators=(",", ":")))

    out_path = pathlib.Path(args.out)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
