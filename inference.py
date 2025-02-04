import argparse
import json
import os
import random

import numpy as np
import torch
from peft import PeftConfig, PeftModel
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from aria.load_video import load_video
from aria.lora.layers import GroupedGemmLoraLayer
from aria.model import AriaForConditionalGeneration, AriaProcessor, GroupedGEMM

# Add command-line argument parsing
parser = argparse.ArgumentParser(description="Newlab inference")
parser.add_argument(
    "--base_model_path", type=str, required=True, help="Path to the base model"
)
parser.add_argument(
    "--peft_model_path", type=str, default=None, help="Path to the PEFT model"
)
parser.add_argument(
    "--tokenizer_path", type=str, required=True, help="Path to the tokenizer"
)
parser.add_argument(
    "--save_root", type=str, required=True, help="The root path of output."
)
parser.add_argument("--image_size", type=int, default=980, help="Maximum image size")
parser.add_argument(
    "--batch_size", type=int, default=1, help="Batch size for evaluation"
)
parser.add_argument(
    "--num_workers", type=int, default=8, help="Number of workers for data loading"
)

args = parser.parse_args()
os.makedirs(args.save_root, exist_ok=True)


class NextQA_Dataset(Dataset):
    def __init__(self):
        super().__init__()
        annos = "/home/ec2-user/DATA_s3/NewlabDataset/temp_aria_data_files/only_gloss_and_translation/test_multilingual_3.jsonl"
        vis_root = "/home/ec2-user/DATA_s3/NewlabDataset/"

        self.dataset = []
        lines = open(annos).readlines()
        for line in tqdm(lines):
            anno = json.loads(line.strip())
            anno["video"]["path"] = os.path.join(vis_root, anno["video"]["path"])
            self.dataset.append(anno)

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        return self.dataset[idx]


def load_model_and_tokenizer(args):
    processor = AriaProcessor.from_pretrained(
        args.base_model_path, tokenizer_path=args.tokenizer_path
    )
    processor.tokenizer.padding_side = "left"
    tokenizer = processor.tokenizer

    model = AriaForConditionalGeneration.from_pretrained(
        args.base_model_path, device_map="auto", torch_dtype=torch.bfloat16
    ).eval()
    model.pad_token_id = tokenizer.pad_token_id

    if args.peft_model_path:
        peft_config = PeftConfig.from_pretrained(args.peft_model_path)
        custom_module_mapping = {GroupedGEMM: GroupedGemmLoraLayer}
        peft_config._register_custom_module(custom_module_mapping)
        model = PeftModel.from_pretrained(
            model,
            args.peft_model_path,
            config=peft_config,
            is_trainable=False,
            autocast_adapter_dtype=False,
        )

    return model, tokenizer, processor


def process_batch(model, tokenizer, inputs, original_batch, prompts):
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    inputs["pixel_values"] = inputs["pixel_values"].to(model.dtype)
    with torch.inference_mode(), torch.cuda.amp.autocast(dtype=torch.bfloat16):
        output = model.generate(
            **inputs,
            max_new_tokens=512,
            stop_strings=["<|im_end|>"],
            tokenizer=tokenizer,
        )

    for i, prompt in enumerate(prompts):
        prompt_len = len(inputs["input_ids"][i])
        output_text = tokenizer.decode(
            output[i][prompt_len:], skip_special_tokens=True
        ).replace("<|im_end|>", "")
        original_batch[i]["pred"] = output_text

    return original_batch


def collate_fn(batch, processor, tokenizer):
    messages = []
    images = []
    for item in batch:
        images.extend(load_video(item["video"]["path"], item["video"]["num_frames"]))
        user_message = [msg for msg in item["messages"] if msg["role"] == "user"]
        for message in user_message:
            for cont_idx, cont in enumerate(message["content"]):
                if cont["type"] == "video":
                    del message["content"][cont_idx]
                    for img_i in range(item["video"]["num_frames"]):
                        insert_item = {
                            "text": None,
                            "type": "image",
                        }
                        message["content"].insert(cont_idx + img_i, insert_item)
        messages.append(user_message)

    texts = [
        processor.apply_chat_template(msg, add_generation_prompt=True)
        for msg in messages
    ]

    inputs = processor(
        text=texts,
        images=images,
        return_tensors="pt",
        padding="longest",
        max_image_size=args.image_size,
    )

    return inputs, batch, texts


def main():
    model, tokenizer, processor = load_model_and_tokenizer(args)

    # breakpoint()

    dataset = NextQA_Dataset()
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=lambda batch: collate_fn(batch, processor, tokenizer),
    )

    results_file = f"{args.save_root}/inference_multilingual3.json"
    # Initialize empty results file
    with open(results_file, "w") as fo:
        json.dump([], fo)

    # results = []
    for batch in tqdm(dataloader, desc="Processing batches"):
        inputs, original_batch, prompts = batch
    #     results.extend(process_batch(model, tokenizer, inputs, original_batch, prompts))  
    #     with open(f"{args.save_root}/nextqa_result.json", "w") as fo:
    #         json.dump(results, fo, indent=4, ensure_ascii=False)
    
    # return results
        batch_results = process_batch(model, tokenizer, inputs, original_batch, prompts)

        #  Process and append new results for this batch
        new_results = []
        for result in batch_results:
            new_json = {
                "video": result["video"],
                "ground_truth": result['messages'][-1]['content'][0]['text'],
                "pred": result["pred"],
            }
            new_results.append(new_json)

        # Read existing results
        with open(results_file, "r") as fi:
            all_results = json.load(fi)
        
        # Append new results and write back
        all_results.extend(new_results)
        with open(results_file, "w") as fo:
            json.dump(all_results, fo, indent=4, ensure_ascii=False)

    return all_results

if __name__ == "__main__":
    output = main()
    print(output)
