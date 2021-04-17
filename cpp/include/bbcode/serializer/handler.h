#ifndef BBCODE_HANDLER_H
#define BBCODE_HANDLER_H

#include "./option.h"
#include "./stream.h"

/*!
 * Class Handler Module
 *
 * Process the high-level data structure object, such as
 *  array, pair, set, ... etc. Using the extra `Option`
 *  configuration to control the `Read` and `Write` format
 *  logic.
 *
 * Basicly, the handler is based on the `Stream` class to
 *  process the basic c++ native type, including three
 *  types mainly:
 *
 *  - ARITHMETIC, more details refer to `types.h` please,
 *      which contains the exhaustive condition trigger logic.
 *  - STRING, c++ string compatiable type.
 *  - POINTER, pointer handler logic.
 *      
 *
 * Main interface
 *
 *  - TypeHandler, abstract data type, configure the
 *      default options for some structure.
 *
 *      supported functions:
 *      + config_option_default(), highly level to invoke
 *        the initiate function before serialize.
 *
 *  - Handler, process the specific data type, instaniated
 *      with data type name.
 *
 *      supported function:
 *      + [optional] sub_handler<index>(), 
 *      + option(), get the option for current handler.
 *      + Read(BaseStream&, T*),
 *      + Write(BaseStream&, T const&),
 *
 */
namespace bbcode {

namespace details {

template<int type>
class _TypeHandler {
protected:
  static Options& init_option_default() {
    option_default()
      .register_option("prefix", "")
      .register_option("suffix", "")
      .register_option("ignore", "");
    return option_default();
  }

  template<typename ...Args>
  static void register_option(Options &opts, Args && ...args) {
    opts.register_option(args...);
  }
  
  Options option_;

public:
  _TypeHandler() : option_(option_default()) {}

  // virtual void list_options() = 0;
  inline Options& option() { return option_; }
  static Options& option_default() { 
    static Options opts_def;
    return opts_def;
  }
};

} // namespace details

template<int type>
class TypeHandler : public details::_TypeHandler<type> {
public:
  static void config_option_default() {
    details::_TypeHandler<type>::init_option_default();
  }
};    

/*!
 * Specific Handler Class
 *
 * Declaration:
 *  template<typename T, int type>
 *  Class Handler : public TypeHandler<type>;
 *
 * Methods to be implemented:
 *
 *  - template<size_t index> RT& sub_handler(size_t)
 *    SFINAE: "Substitution Failure Is Not An Error"
 *      using the mechanism to implement different return handler
 *      types and choose appropriate sub_handler specialization.
 *
 *  - virtual void Write(BaseStream&, T const&)
 *    write serialized stream
 */
template<typename T, int type = TYPE_VALUE(T)>
class Handler : public TypeHandler<type> { };

template<typename T>
class Handler<T, FormatType::ARITHMETIC>
  : public TypeHandler<FormatType::ARITHMETIC> {
public:
  virtual void Write(BaseStream &os, T const& data) {
    os.Write(option_.option<std::string>("prefix"));
    os.Write(data);
    os.Write(option_.option<std::string>("suffix"));
  }
};

template<typename T>
class Handler<T, FormatType::STRING>
  : public TypeHandler<FormatType::STRING> {
public:
  virtual void Write(BaseStream &os, T const& data) {
    os.Write(option_.option<std::string>("prefix"));
    os.Write(data);
    os.Write(option_.option<std::string>("suffix"));
  }
};

template<>
class TypeHandler<FormatType::ARRAY> : public details::_TypeHandler<FormatType::ARRAY> {
public:
  static void config_option_default() {
    init_option_default()
      .register_option("inner_split", ",")
      .config_option("prefix", "[")
      .config_option("suffix", "]");
  }
};

template<typename T>
class Handler<T, FormatType::ARRAY>
  : public TypeHandler<FormatType::ARRAY> {

  using vtype = typename T::value_type;
  Handler<vtype> recur_handler_;

public:
  template<size_t index = 0>
  typename std::enable_if<index == 0, Handler<vtype>&>::type
  sub_handler() { return recur_handler_; }

  Handler() : TypeHandler(),
              recur_handler_(Handler<vtype, TYPE_VALUE(vtype)>())
  {}

  virtual void Write(BaseStream &os, T const& data) {
    os.Write(option_.option<std::string>("prefix"));
    for (auto &&it = data.begin(); it != data.end(); ++it) {
      if (it != data.begin())
        os.Write(option_.option<std::string>("inner_split"));
      recur_handler_.Write(os, *it);
    }
    os.Write(option_.option<std::string>("suffix"));
  }
};


template<>
class TypeHandler<FormatType::PAIR>
  : public details::_TypeHandler<FormatType::PAIR> {
public:
  static void config_option_default() {
    init_option_default()
      .register_option("inner_split", ",")
      .config_option("prefix", "(")
      .config_option("suffix", ")");
  }
};

template<typename T>
class Handler<T, FormatType::PAIR>
  : public TypeHandler<FormatType::PAIR> {

  using fir_type = typename T::first_type;
  using sec_type = typename T::second_type;

  Handler<fir_type> fir_handler_;
  Handler<sec_type> sec_handler_;

public:
  // SFINAE: "Substitution Failure Is Not An Error"
  template<size_t index>
  typename std::enable_if<index == 0, Handler<fir_type>&>::type
  sub_handler() { return fir_handler_; }

  template<size_t index>
  typename std::enable_if<index == 1, Handler<sec_type>&>::type 
  sub_handler() { return sec_handler_; }

  Handler() : TypeHandler(),
              fir_handler_(Handler<fir_type>()),
              sec_handler_(Handler<sec_type>())
  {}

  virtual void Write(BaseStream &os, T const& data) {
    os.Write(option_.option<std::string>("prefix"));
    fir_handler_.Write(os, data.first);
    os.Write(option_.option<std::string>("inner_split"));
    sec_handler_.Write(os, data.second);
    os.Write(option_.option<std::string>("suffix"));
  }
};

template<>
class TypeHandler<FormatType::POINTER>
  : public details::_TypeHandler<FormatType::POINTER> {
public:
  static void config_option_default() {
    init_option_default()
      .register_option("skip_pointer", 0)
      .register_option("p_prefix", "<")
      .register_option("p_middle", ">&{")
      .register_option("p_suffix", "}");
  }
};

template<typename T>
class Handler<T*, FormatType::POINTER>
  : public TypeHandler<FormatType::POINTER> {
  Handler<T> sub_handler_;

public:
  template<size_t index = 0>
  typename std::enable_if<index == 0, Handler<T>&>::type
  sub_handler() { return sub_handler_; }

  Handler() : TypeHandler(),
              sub_handler_(Handler<T>())
  {}

  virtual void Write(BaseStream &os, T* const& data) {
    os.Write(option_.option<std::string>("prefix"));
    if (!option_.option<int>("skip_pointer")) {
      os.Write(option_.option<std::string>("p_prefix"))
        .Write(data)
        .Write(option_.option<std::string>("p_middle"));
    }
    sub_handler_.Write(os, *data);
    if (!option_.option<int>("skip_pointer"))
      os.Write(option_.option<std::string>("p_suffix"));
    os.Write(option_.option<std::string>("suffix"));
  }
};

template<>
class Handler<std::nullptr_t, FormatType::POINTER>
  : public TypeHandler<FormatType::POINTER> {
public:
  virtual void Write(BaseStream &os, std::nullptr_t) {
    os.Write(option_.option<std::string>("prefix"))
      .Write("nullptr")
      .Write(option_.option<std::string>("suffix"));
  }
};

void init_handler() {
  TypeHandler<FormatType::ARITHMETIC>::config_option_default();
  TypeHandler<FormatType::STRING>::config_option_default();
  TypeHandler<FormatType::ARRAY>::config_option_default();
  TypeHandler<FormatType::PAIR>::config_option_default();
  TypeHandler<FormatType::POINTER>::config_option_default();
  TypeHandler<FormatType::CLASS>::config_option_default();
  TypeHandler<FormatType::ENUMERATE>::config_option_default();
}


} // namespace bbcode

#endif // BBCODE_HANDLER_H
