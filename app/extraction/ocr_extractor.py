from pathlib import Path
from typing import Dict, Any

import torch
from transformers import AutoProcessor, AutoModelForImageTextToText

class OCRExtractor:
    def __init__(
        self,
        glm_model_dir: str,
        task: str = "text",
    ):
        self.glm_model_dir = str(Path(glm_model_dir).expanduser().resolve())
        self.task = task

        self.processor = AutoProcessor.from_pretrained(
            self.glm_model_dir,
            local_files_only=True,
        )

        self.model = AutoModelForImageTextToText.from_pretrained(
            self.glm_model_dir,
            torch_dtype="auto",
            device_map="auto",
            local_files_only=True,
        )
    # Basit bir prompt builder, farklı görevler için farklı prompt'lar dönebilir.
    def _build_prompt(self) -> str:
        prompt_map = {
            "text": "Text Recognition:",
            "table": "Table Recognition:",
        }
        return prompt_map.get(self.task, "Text Recognition:")

    # GLM tabanlı OCR çıkarımı
    def _run_glm_ocr(self, image_path: Path) -> str:
        user_prompt = self._build_prompt()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "url": str(image_path)},
                    {"type": "text", "text": user_prompt},
                ],
            }
        ]

        inputs = self.processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device)

        inputs.pop("token_type_ids", None)

        with torch.no_grad():
            generated_ids = self.model.generate(**inputs, max_new_tokens=2048)

        new_tokens = generated_ids[0][inputs["input_ids"].shape[1]:]
        decoded = self.processor.decode(new_tokens, skip_special_tokens=True).strip()

        return decoded
    
    # Dışarıya açık metot, görüntü yolunu alır ve OCR sonucunu döner.
    def extract_text_from_image(self, image_path: str | Path) -> Dict[str, Any]:
        image_path = Path(image_path)

        text = self._run_glm_ocr(image_path)

        return {
            "page_number": 1,
            "text": text,
            "source_file": image_path.name,
            "extraction_method": "glm_ocr",
        }