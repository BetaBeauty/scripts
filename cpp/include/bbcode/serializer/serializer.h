#ifndef CODE_SERIALIZER_H
#define CODE_SERIALIZER_H

#include "./handler.h"

namespace bbcode {

template<typename T>
std::string serialize(T *t) {
  ERROR() << "to be implemented";
  return "";
  // std::ostringstream os;
  // Handler<T>::to_string(os, *t);
  // return os.str();
}


template<template<typename, int> class H, typename T>
class Formater {
  T const& data_;
  std::shared_ptr<BaseStream> os_;
  H<T, TYPE_VALUE(T)> handler_;

public:
  Formater(T const& data)
    : data_(data),
      handler_(H<T, TYPE_VALUE(T)>())
  {}

  template<typename S,
           typename std::enable_if<ConvertFromTo<S, BaseStream>
              ::value>::type* = nullptr>
  Formater& compose(S &os) {
    os_ = std::shared_ptr<BaseStream>(&os, &null_deleter<BaseStream>);
    return *this;
  }
  template<typename S,
           typename std::enable_if<ConvertFromTo<S, BaseStream>
              ::value>::type* = nullptr>
  Formater& compose(S &&os) {
    os_ = std::make_shared<S>(std::move(os));
    return *this;
  }

  H<T, TYPE_VALUE(T)>& handler() { return handler_; }

  void Write() {
    if (os_ == nullptr) os_ = std::make_shared<IOStream>();
    handler_.Write(*os_, data_);
  }

  void Writeln() {
    Write();
    (*os_).Write("\n");
  }
};

class Serializer {
public:
  static void init() { init_handler(); }
  
  template<int type>
  static Options& option_default() {
    return TypeHandler<type>::option_default();
  }

  template<
    template<typename, int> class H = Handler, typename T>
  static Formater<H, T> generate(T const& a) {
    return Formater<H, T>(a);
  }
};


}

#endif // CODE_SERIALIZER_H
