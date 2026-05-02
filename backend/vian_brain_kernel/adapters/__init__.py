"""
adapters/__init__.py — Vian Brain Kernel Adapters (WO-003)
외부 언어 모델 어댑터 패키지.

[주의] 금지: 이 패키지에서 brain_final_response 설정 / 이유: Ollama는 언어 근육, 최종 판단자 아님
[의존성] 연결: VianBrainKernel.process() / WO-004+에서 kernel.py가 adapter를 호출
"""
from backend.vian_brain_kernel.adapters.ollama_adapter import OllamaAdapter, OllamaResult

__all__ = ["OllamaAdapter", "OllamaResult"]
