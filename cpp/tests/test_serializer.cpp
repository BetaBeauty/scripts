#include <iostream>

#include <bbcode/serializer/types.h>
#include <bbcode/serializer/serializer.h>

using namespace bbcode;

int main() {
  Options f;

  f.register_option("ident_str", "hello world");
  std::cout << f.option<std::string>("ident_str") << std::endl;

  Options g = f;
  std::cout << g.option<std::string>("ident_str") << std::endl;

  g.config_option("ident_str", "no world");
  std::cout << f.option<std::string>("ident_str") << std::endl;

  std::cout << g.option<std::string>("ident_str") << std::endl;
  
  Serializer::init();

  // Serializer::option_default<FormatType::ARRAY>()
    // .print()
    // .config_option("inner_split", "|");

  std::vector<std::pair<std::string, int>> a{
    {"hello", 0},
    {"world", 1}
  };

  std::vector<std::string> b {
    "hello", "world", "to", "me"
  };

  Serializer::generate<Handler>(&a)
    .compose(IOStream())
    .Writeln();

  Serializer::generate(nullptr)
    .Writeln();


  std::vector<std::pair<std::string, std::vector<int>>> c{
    {"one", {1,2,3,}},
    {"two", {4,5,6,}},
    {"three", {7,8,9,}}
  };
  auto &&test = Serializer::generate(&c);
  test.handler().option()
    .print()
    .config_option("p_middle", "> &{\n  ")
    .config_option("p_suffix", "\n}");
  test.handler()
    .sub_handler()
    .sub_handler()
    .sub_handler<0>()
    .option()
    .print()
    .config_option("prefix", "S:");
  test.handler()
    .sub_handler()
    .sub_handler()
    .sub_handler<1>()
    .sub_handler()
    .option()
    .print()
    .config_option("prefix", "I:");
  test.Writeln();


  Formater<Handler, decltype(a)> formater(a);
  formater.handler().sub_handler().sub_handler<1>()
    .option()
    .config_option("prefix", "Int(")
    .config_option("suffix", ")");
  // writer.compose(std::cout).Write();
  formater.compose(IOStream());
  IOStream stream;
  formater.compose(stream);
  formater.Writeln();

  return 0;
}
