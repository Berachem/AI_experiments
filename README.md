```
██████╗ ███████╗██████╗  █████╗ ███╗   ███╗██╗███╗   ██╗██████╗
██╔══██╗██╔════╝██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗
██████╔╝█████╗  ██████╔╝███████║██╔████╔██║██║██╔██╗ ██║██║  ██║
██╔══██╗██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██║██║╚██╗██║██║  ██║
██████╔╝███████╗██║  ██║██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██████╔╝
╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═════╝
```

# AI_models : PoC

## ✨ Normalization (AI_Normalization.py)

**This proof of concept (PoC) explores the idea of using two Ollama AI models to generate and improve responses on a given topic (OSINT in this example).**  
The ultimate goal is to fine-tune the generating model with the corrected responses from a more powerful model to enhance its performance.

### 🎯 Features

This script allows you to:

- 📝 **Generate** a response to a given question using a base model (**llama3.2**).
- 🔄 **Correct and improve** this response using a more advanced model (**deepseek-r1:14b**).
- 💾 **Save** the results as a JSON dataset for future fine-tuning.

### 🛠️ Technical Details

- **Language**: Python
- **AI Framework**: Ollama
- **Models used**:
  - **Generator**: llama3.2 (model to be fine-tuned)
  - **Corrector**: deepseek-r1:14b (more powerful model)

### 🚀 Possible Improvements

- ✅ **Mass Generation**: Increase `N_EXAMPLES` to produce a larger dataset.
- ✅ **AI vs AI Comparison**: Add an evaluation of the differences between the generated and corrected responses.
- ✅ **Automatic Verification**: Integrate an algorithm that checks if the correction actually brings an improvement.

## Installation & usage

1. install ollama from the official website: https://ollama.com/

2. install the requirements:

```bash
pip install -r requirements.txt
```

3. run the script:

```bash
python [POC_NAME].py
```
