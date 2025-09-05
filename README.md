## DSL pipeline generation 

This project aims to automate DSL generation for any domain. Currently, we are working with the craft domain. 


## Example of command to run funsearch:

python3 -m funsearch.implementation.funsearch --model_type ollama --function craft --spec_file  prompt_specifications/specification_jocelyn.txt --function_init craft_func_init.py
## Acknowledgements

- [@jacobandreas](https://github.com/jacobandreas) for open-sourcing the mine-craft inspired Craft Environment used in Policy Sketches paper [[1]](##References) [Craft Environment](https://github.com/jacobandreas/psketch) which this codebase is heavily based on

## References

* [1] [Modular Multitask Reinforcement Learning with Policy Sketches](https://arxiv.org/abs/1611.01796) (Andreas et al., 2016)
